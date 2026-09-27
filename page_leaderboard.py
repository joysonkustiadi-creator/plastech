import streamlit as st
from database_manager import DatabaseManager

def render_leaderboard_page(db, user):
    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">🏆 Leaderboard</div>', unsafe_allow_html=True)
    
    st.markdown("### 👑 Top Kontributor PlasTech")
    
    leaderboard = db.get_leaderboard(10)
    
    if not leaderboard.empty:
        for idx, row in leaderboard.iterrows():
            rank = idx + 1
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                st.markdown(f"### {medal}")
            
            with col2:
                is_current_user = row['username'] == user['username']
                username_display = f"**{row['username']}** (Anda)" if is_current_user else row['username']
                st.markdown(f"### {username_display}")
                st.caption(f"📦 {row['total_disposed']} sampah dibuang")
            
            with col3:
                st.markdown(f"### 🎁 {row['points']} poin")
            
            st.markdown("---")
    else:
        st.info("Belum ada data di leaderboard. Jadilah yang pertama!")