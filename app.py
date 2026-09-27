import streamlit as st
from config import Config
from database_manager import DatabaseManager
from yolo_detector import WasteDetector
from sidebar import render_sidebar
from page_login import render_login_page
from page_home import render_home_page
from page_detect import render_detect_page
from page_dispose import render_dispose_page
from page_leaderboard import render_leaderboard_page
from page_profile import render_profile_page

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.feature-card {
    background: #ffffff !important;
    border-radius: 18px;
    padding: 25px;
    height: 220px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    color: #222222 !important;
}

.feature-card h3 {
    color: #2E7D32 !important;
    font-size: 1.6rem;
    font-weight: 700;
}

.feature-card p {
    font-size: 1rem;
    color: #555555 !important;
}

</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    if 'detector' not in st.session_state:
        st.session_state.detector = WasteDetector()

def main():
    init_session_state()
    
    db = st.session_state.db
    detector = st.session_state.detector
    
    if not st.session_state.logged_in:
        render_login_page(db)
    else:
        user = st.session_state.user

        updated = db.get_user_by_id_simple(user['id'])
        if updated:
            st.session_state.user['points'] = updated['points']

        render_sidebar(user)
        page = st.session_state.current_page
        
        if page == "home":
            render_home_page(db, user)
        elif page == "detect":
            render_detect_page(db, user, detector)
        elif page == "dispose":
            render_dispose_page(db, user)
        elif page == "leaderboard":
            render_leaderboard_page(db, user)
        elif page == "profile":
            render_profile_page(db, user)

if __name__ == "__main__":
    main()