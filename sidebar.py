import streamlit as st

def render_sidebar(user):
    with st.sidebar:
        st.markdown("## 🧭 Navigasi")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.current_page = "leaderboard"
            st.rerun()
        
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**User:** {user['username']}")
        st.markdown(f"**Poin:** 🎁 {user['points']}")