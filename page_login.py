import streamlit as st
from database_manager import DatabaseManager
from auth import hash_password

def render_login_page(db):
    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">♻️ PlasTech</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:1.2rem; color:#666;">Smart Waste Management System</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        # ===========================
        # LOGIN
        # ===========================
        with tab1:
            st.subheader("Login ke Akun Anda")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary"):
                if username and password:
                    user = db.get_user(username, hash_password(password))
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = {
                            'id': user['id'],
                            'username': user['username'],
                            'points': user['points']
                        }
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")
                else:
                    st.warning("Mohon isi semua field!")
        
        # ===========================
        # REGISTER
        # ===========================
        with tab2:
            st.subheader("Buat Akun Baru")
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Konfirmasi Password", type="password")
            
            if st.button("Register", type="primary"):
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        if db.create_user(new_username, hash_password(new_password)):
                            st.success("Registrasi berhasil! Silakan login.")
                        else:
                            st.error("Username sudah digunakan!")
                    else:
                        st.error("Password tidak cocok!")
                else:
                    st.warning("Mohon isi semua field!")