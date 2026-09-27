import streamlit as st
from database_manager import DatabaseManager

def render_profile_page(db, user):
    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">👤 Profile</div>', unsafe_allow_html=True)
    user_data = db.get_user_by_id(user['id'])
    stats = db.get_user_stats(user['id'])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("""
        <div style='text-align:center; padding:2rem; background:#f0f0f0; border-radius:15px;'>
            <div style='font-size:5rem;'>👤</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"## {user_data['username']}")
        st.markdown(f"**Member sejak:** {user_data['created_at']}")
        st.markdown(f"### 🏆 {user_data['points']} Poin")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📸 Total Deteksi", stats['detected'])

    with col2:
        st.metric("✅ Sampah Dibuang", stats['disposed'])

    with col3:
        success_rate = (stats['disposed'] / stats['detected'] * 100) if stats['detected'] > 0 else 0
        st.metric("📊 Success Rate", f"{success_rate:.1f}%")

    st.markdown("---")

    st.markdown("### 📜 Riwayat Aktivitas")

    activity = db.get_user_detections(user['id'], 10)

    if not activity.empty:
        for idx, row in activity.iterrows():
            status_emoji = "✅" if row['status'] == 'disposed' else "⏳" if row['status'] == 'pending' else "❌"
            status_text = "Dibuang" if row['status'] == 'disposed' else "Pending" if row['status'] == 'pending' else "Expired"
            
            st.markdown(f"""
            **{status_emoji} {row['waste_type'].title()}** - {row['points']} poin | {status_text}  
            📅 {row['detected_at']}
            """)
            st.markdown("---")
    else:
        st.info("Belum ada aktivitas. Mulai deteksi sampah sekarang!")

    if st.button("🚪 Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_page = "home"
        st.rerun()