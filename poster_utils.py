import os
import json
import base64
import html
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "poster_cache.json"

def load_disk_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_disk_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass

POSTER_DISK_CACHE = load_disk_cache()

DEFAULT_TMDB_KEYS = [
    key for key in [
        os.getenv("TMDB_API_KEY_1"),
        os.getenv("TMDB_API_KEY_2"),
    ] if key
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def generate_fallback_poster_svg(title: str, year: str = "", genre: str = "Movie", rating: str = "7.5") -> str:
    """Generate a clean, base64-encoded WatchWise SVG poster Data URI."""
    title_short = title[:24] + ("..." if len(title) > 24 else "")
    title_esc = html.escape(title_short)
    genre_esc = html.escape(genre[:20] if genre else "Movie")
    year_esc = html.escape(str(year))
    rating_esc = html.escape(str(rating))
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="750" viewBox="0 0 500 750">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0f172a"/>
          <stop offset="50%" stop-color="#1e293b"/>
          <stop offset="100%" stop-color="#0b0e14"/>
        </linearGradient>
        <linearGradient id="brand" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#00a8e1"/>
          <stop offset="100%" stop-color="#3b82f6"/>
        </linearGradient>
      </defs>
      <rect width="500" height="750" fill="url(#bg)"/>
      <rect x="0" y="0" width="500" height="12" fill="url(#brand)"/>
      
      <!-- WatchWise Badge -->
      <rect x="25" y="30" width="140" height="34" rx="6" fill="#00a8e1"/>
      <text x="95" y="53" fill="#ffffff" font-family="'Segoe UI', Roboto, Helvetica, sans-serif" font-size="14" font-weight="800" text-anchor="middle" letter-spacing="1">WATCHWISE</text>
      
      <!-- Graphic Play Icon -->
      <circle cx="250" cy="290" r="70" fill="#1e293b" stroke="#00a8e1" stroke-width="3" opacity="0.9"/>
      <polygon points="238,262 276,290 238,318" fill="#00a8e1"/>
      
      <!-- Movie Title & Subtitle -->
      <text x="250" y="430" fill="#ffffff" font-family="'Segoe UI', Roboto, Helvetica, sans-serif" font-size="24" font-weight="bold" text-anchor="middle">{title_esc}</text>
      <text x="250" y="470" fill="#94a3b8" font-family="'Segoe UI', Roboto, Helvetica, sans-serif" font-size="16" text-anchor="middle">{year_esc} • {genre_esc}</text>
      
      <!-- IMDb Rating Badge -->
      <rect x="200" y="510" width="100" height="34" rx="6" fill="#f5c518"/>
      <text x="250" y="533" fill="#000000" font-family="'Segoe UI', Roboto, Helvetica, sans-serif" font-size="16" font-weight="bold" text-anchor="middle">★ {rating_esc}</text>
      
      <!-- Footer -->
      <text x="250" y="690" fill="#64748b" font-family="'Segoe UI', Roboto, Helvetica, sans-serif" font-size="13" text-anchor="middle">WATCHWISE RECOMMENDED</text>
    </svg>"""
    
    b64_svg = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_svg}"

def fetch_single_poster(item: dict) -> tuple:
    """Fetch poster URL for a single movie with 0.3s strict timeout or return fallback."""
    m_id = str(item.get('movie_id', 0))
    title = item.get('title', '')
    year = item.get('year', '')
    genre = item.get('genre', '')
    rating = item.get('rating', '7.0')

    # Check local disk cache first
    if m_id in POSTER_DISK_CACHE and POSTER_DISK_CACHE[m_id] and not POSTER_DISK_CACHE[m_id].startswith("data:image/svg+xml;utf8"):
        return (m_id, POSTER_DISK_CACHE[m_id])

    # Try quick TMDB API call with 0.3s strict timeout
    if m_id and m_id != "0":
        for api_key in DEFAULT_TMDB_KEYS[:1]:
            try:
                url = f"https://api.themoviedb.org/3/movie/{m_id}?api_key={api_key}&language=en-US"
                res = requests.get(url, headers=HEADERS, timeout=0.3)
                if res.status_code == 200:
                    poster_path = res.json().get('poster_path')
                    if poster_path:
                        img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        POSTER_DISK_CACHE[m_id] = img_url
                        return (m_id, img_url)
            except Exception:
                pass

    # Clean Base64 Fallback SVG
    fallback_url = generate_fallback_poster_svg(title, year, genre, rating)
    POSTER_DISK_CACHE[m_id] = fallback_url
    return (m_id, fallback_url)

def fetch_poster_url(movie_id: int, title: str, year: str = "", genre: str = "Movie", rating: str = "7.0") -> str:
    item = {
        'movie_id': str(movie_id),
        'title': title,
        'year': year,
        'genre': genre,
        'rating': rating
    }
    _, url = fetch_single_poster(item)
    return url

def fetch_posters_batch(items: list) -> dict:
    results = {}
    items_to_fetch = []

    for item in items:
        m_id = str(item.get('movie_id', 0))
        if m_id in POSTER_DISK_CACHE and not POSTER_DISK_CACHE[m_id].startswith("data:image/svg+xml;utf8"):
            results[m_id] = POSTER_DISK_CACHE[m_id]
        else:
            items_to_fetch.append(item)

    if items_to_fetch:
        with ThreadPoolExecutor(max_workers=len(items_to_fetch)) as executor:
            future_to_item = {executor.submit(fetch_single_poster, item): str(item.get('movie_id', 0)) for item in items_to_fetch}
            for future in as_completed(future_to_item):
                m_id = future_to_item[future]
                try:
                    res_id, url = future.result()
                    results[res_id] = url
                except Exception:
                    results[m_id] = generate_fallback_poster_svg("Movie", "", "", "7.0")

        save_disk_cache(POSTER_DISK_CACHE)

    return results

__all__ = ['fetch_posters_batch', 'fetch_poster_url', 'generate_fallback_poster_svg']
