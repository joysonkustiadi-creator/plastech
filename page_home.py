import streamlit as st
from stats_card import render_stats_card, render_feature_card
from database_manager import DatabaseManager

def render_home_page(db, user):

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
        color: #444444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">🏠 Dashboard PlasTech</div>', unsafe_allow_html=True)
    
    st.markdown(f"### Selamat datang, **{user['username']}**! 👋")
    
    stats = db.get_user_stats(user['id'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_stats_card("Total Poin Anda", user['points'], "🏆")
    with col2:
        render_stats_card("Sampah Pending", stats['pending'], "⏳")
    with col3:
        render_stats_card("Sampah Dibuang", stats['disposed'], "✅")
    
    st.markdown("---")
    
    st.markdown("## 🎯 Fitur Utama")
    
    col1, col2 = st.columns(2)

    # ==== CARD 1 ====
    with col1:
        render_feature_card(
            "Deteksi Sampah",
            "Deteksi sampah plastik menggunakan AI dan dapatkan poin! Jangan lupa buang dalam waktu 24 jam.",
            "📸"
        )
        if st.button("🎥 Mulai Deteksi", key="detect_btn", type="primary"):
            st.session_state.current_page = "detect"
            st.rerun()

    # ==== CARD 2 ====
    with col2:
        render_feature_card(
            "Buang Sampah",
            "Scan QR di tempat pembuangan dan upload foto bukti untuk mengklaim poin Anda.",
            "🗑️"
        )
        if st.button("📷 Buang Sampah", key="dispose_btn", type="primary"):
            st.session_state.current_page = "dispose"
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 💡 Cara Kerja PlasTech")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**1. DETEKSI** 📸\n\nFoto sampah plastik yang Anda temukan")
    with col2:
        st.warning("**2. BUANG** 🗑️\n\nBuang ke tempat sampah dalam 24 jam")
    with col3:
        st.success("**3. POIN** 🎁\n\nDapatkan poin dan naik ranking!")