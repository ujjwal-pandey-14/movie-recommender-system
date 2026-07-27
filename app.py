import streamlit as st
import pickle
import pandas as pd
from poster_utils import fetch_posters_batch

# Page configuration for WatchWise
st.set_page_config(
    page_title="WatchWise | Movie Recommender",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load pickled model files safely
@st.cache_resource
def load_data():
    movies_df = pickle.load(open('movies.pkl', 'rb'))
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity_matrix

try:
    movies, similarity = load_data()
except Exception as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

# Inject Dark WatchWise Amazon Prime Inspired CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0b0e14 !important;
        color: #e2e8f0 !important;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(11, 14, 20, 0.95) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Navbar */
    .watchwise-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 28px;
        background: linear-gradient(180deg, #0f172a 0%, #0b0e14 100%);
        border-bottom: 2px solid #00a8e1;
        margin-bottom: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 168, 225, 0.18);
    }
    
    .watchwise-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    
    .watchwise-logo span {
        color: #00a8e1;
    }
    
    .watchwise-badge {
        background: #00a8e1;
        color: #ffffff;
        font-size: 11px;
        font-weight: 900;
        padding: 3px 9px;
        border-radius: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .watchwise-nav-links {
        display: flex;
        gap: 25px;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .watchwise-nav-item {
        color: #94a3b8;
        font-size: 15px;
        font-weight: 600;
    }

    .watchwise-nav-item.active {
        color: #00a8e1;
    }

    /* Hero Spotlight Box */
    .hero-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 60%, #0b0e14 100%);
        border-radius: 14px;
        padding: 28px;
        margin-bottom: 25px;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .hero-tag {
        display: inline-block;
        background: rgba(0, 168, 225, 0.2);
        color: #00a8e1;
        border: 1px solid #00a8e1;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 10px 0;
        line-height: 1.2;
    }

    .hero-meta {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 14px;
        font-size: 14px;
        color: #94a3b8;
    }

    .rating-pill {
        background: #f5c518;
        color: #000000;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 13px;
    }

    .quality-tag {
        border: 1px solid #64748b;
        color: #cbd5e1;
        padding: 1px 6px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 600;
    }

    .hero-desc {
        font-size: 15px;
        color: #cbd5e1;
        line-height: 1.6;
        max-width: 900px;
    }

    /* Section Headers */
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
        margin: 20px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-header::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 22px;
        background: #00a8e1;
        border-radius: 2px;
    }

    /* Movie Cards */
    .movie-card {
        background: #1e293b;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #334155;
        transition: all 0.25s ease;
        margin-bottom: 12px;
    }

    .movie-card:hover {
        transform: translateY(-5px);
        border-color: #00a8e1;
        box-shadow: 0 8px 18px rgba(0, 168, 225, 0.25);
    }

    .poster-box {
        position: relative;
        width: 100%;
        padding-top: 145%;
        overflow: hidden;
        background: #0f172a;
    }

    .poster-box img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .card-info {
        padding: 10px 12px;
    }

    .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .card-meta-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
        color: #94a3b8;
    }

    .match-score {
        color: #10b981;
        font-weight: 700;
        font-size: 11px;
    }

    /* Footer */
    .watchwise-footer {
        text-align: center;
        padding: 25px 0 15px 0;
        border-top: 1px solid #1e293b;
        margin-top: 35px;
        color: #64748b;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# Navbar
st.markdown("""
    <div class="watchwise-navbar">
        <div class="watchwise-logo">
            🎬 Watch<span>Wise</span>
            <div class="watchwise-badge">RECOMMENDER</div>
        </div>
        <ul class="watchwise-nav-links">
            <li class="watchwise-nav-item active">Home</li>
            <li class="watchwise-nav-item">Movies</li>
            <li class="watchwise-nav-item">Top Rated</li>
            <li class="watchwise-nav-item">Categories</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🍿 WatchWise Controls")
    num_recommendations = st.slider("Number of Similar Movies", min_value=4, max_value=10, value=6)
    st.markdown("---")
    if st.button("🧹 Clear Cache & Refresh"):
        st.cache_data.clear()
        st.success("Cache cleared!")
    st.markdown("---")
    st.markdown("© 2026 WatchWise Engine")

# Cosine Similarity Engine
def get_recommendation_items(movie_title, num=6):
    matches = movies[movies['title'] == movie_title]
    if matches.empty:
        return []
    
    movie_idx = movies.index.get_loc(matches.index[0])
    distances = similarity[movie_idx]
    
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num+1]
    
    items = []
    for i in movies_list:
        rec_pos = i[0]
        rec_row = movies.iloc[rec_pos]
        
        m_id = str(rec_row.get('movie_id', 0))
        title = str(rec_row.get('title', 'Unknown'))
        overview = str(rec_row.get('overview', 'No synopsis available.'))
        vote_avg = rec_row.get('vote_average', 7.0)
        
        release_date = str(rec_row.get('release_date', ''))
        year = release_date.split('-')[0] if release_date and len(release_date) >= 4 else 'N/A'
        runtime = rec_row.get('runtime', 120)
        
        genres = rec_row.get('genre_list', [])
        genre_str = ", ".join(genres[:2]) if isinstance(genres, list) and len(genres) > 0 else "Movie"
        rating_str = f"{float(vote_avg):.1f}" if pd.notnull(vote_avg) else "7.0"
        
        items.append({
            'movie_id': m_id,
            'title': title,
            'overview': overview,
            'rating': rating_str,
            'year': year,
            'runtime': f"{int(runtime)}m" if pd.notnull(runtime) and runtime > 0 else "120m",
            'genre': genre_str,
            'similarity': round(float(i[1]) * 100, 1)
        })
        
    return items

# Search & Select Input
movie_titles = movies['title'].values
selected_movie = st.selectbox(
    "🔍 Search or select a movie to get WatchWise Recommendations:",
    movie_titles,
    index=0
)

# Render Hero Spotlight
matches = movies[movies['title'] == selected_movie]
if not matches.empty:
    selected_row = matches.iloc[0]
    sel_overview = str(selected_row.get('overview', 'No synopsis available.'))
    sel_vote = selected_row.get('vote_average', 7.5)
    sel_date = str(selected_row.get('release_date', ''))
    sel_year = sel_date.split('-')[0] if sel_date and len(sel_date) >= 4 else 'N/A'
    sel_runtime = selected_row.get('runtime', 120)
    sel_genres = selected_row.get('genre_list', [])
    sel_genre_str = ", ".join(sel_genres[:3]) if isinstance(sel_genres, list) and len(sel_genres) > 0 else "Movie"

    st.markdown(f"""
        <div class="hero-box">
            <div class="hero-tag">🍿 WatchWise Spotlight</div>
            <div class="hero-title">{selected_movie}</div>
            <div class="hero-meta">
                <span class="rating-pill">IMDb {float(sel_vote):.1f}</span>
                <span>{sel_year}</span>
                <span>{int(sel_runtime) if pd.notnull(sel_runtime) else 120} min</span>
                <span class="quality-tag">4K UHD</span>
                <span class="quality-tag">HDR</span>
                <span style="color: #00a8e1; font-weight: 600;">{sel_genre_str}</span>
            </div>
            <div class="hero-desc">{sel_overview}</div>
        </div>
    """, unsafe_allow_html=True)

# Render Recommendations Shelf
st.markdown(f'<div class="section-header">Similar Movies Recommended for "{selected_movie}"</div>', unsafe_allow_html=True)

rec_items = get_recommendation_items(selected_movie, num=num_recommendations)

if rec_items:
    # Parallel batch fetch all posters in <0.3s
    posters = fetch_posters_batch(rec_items)
    
    cols = st.columns(num_recommendations)
    for idx, item in enumerate(rec_items):
        m_id = item['movie_id']
        poster_url = posters.get(m_id, "")
        
        with cols[idx]:
            st.markdown(f"""
                <div class="movie-card">
                    <div class="poster-box">
                        <img src="{poster_url}" alt="{item['title']}" loading="lazy" />
                    </div>
                    <div class="card-info">
                        <div class="card-title" title="{item['title']}">{item['title']}</div>
                        <div class="card-meta-row">
                            <span class="rating-pill">★ {item['rating']}</span>
                            <span class="match-score">{item['similarity']}% match</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📖 Details"):
                st.caption(f"**Year:** {item['year']} | **Runtime:** {item['runtime']}")
                st.caption(f"**Genre:** {item['genre']}")
                st.caption(f"**Synopsis:** {item['overview'][:130]}...")

# Footer
st.markdown("""
    <div class="watchwise-footer">
        WatchWise Recommender Engine • Powered by Cosine Similarity & Content-Based Filtering<br/>
        © 2026 WatchWise. All rights reserved.
    </div>
""", unsafe_allow_html=True)