import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
from database_manager import DatabaseManager
from qr_generator import generate_disposal_qr
from qr_scanner import scan_qr_from_image
from image_processor import image_to_bytes

def render_dispose_page(db, user):
    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">🗑️ Buang Sampah</div>', unsafe_allow_html=True)
    
    if st.button("← Kembali ke Home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    db.expire_old_detections()
    pending = db.get_pending_detections(user['id'])
    
    if pending.empty:
        st.info("📭 Tidak ada sampah yang perlu dibuang.")
        return
    
    st.markdown("### 📋 Daftar Sampah yang Perlu Dibuang")

    for idx, row in pending.iterrows():
        
        expires = pd.to_datetime(row['expires_at'])
        time_left = expires - datetime.now()
        
        if time_left.total_seconds() <= 0:
            continue
        
        hours_left = int(time_left.total_seconds() // 3600)
        minutes_left = int((time_left.total_seconds() % 3600) // 60)

        with st.expander(f"🗑️ {row['waste_type'].title()} - {row['points']} poin | ⏰ {hours_left}h {minutes_left}m"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Terdeteksi:** {row['detected_at']}")
                st.write(f"**Kadaluarsa:** {row['expires_at']}")

                st.markdown("#### 📷 Scan QR Tempat Sampah")

                # ================================
                # 🔥 CAMERA TOGGLE (OPEN/CLOSE)
                # ================================

                cam_key = f"qr_camera_{row['id']}"
                if cam_key not in st.session_state:
                    st.session_state[cam_key] = False

                # Tombol untuk membuka / menutup kamera
                if not st.session_state[cam_key]:
                    if st.button("📷 Mulai Scan QR", key=f"open_cam_{row['id']}"):
                        st.session_state[cam_key] = True
                        st.rerun()
                else:
                    if st.button("❌ Tutup Kamera", key=f"close_cam_{row['id']}"):
                        st.session_state[cam_key] = False
                        st.rerun()

                qr_input = None

                # Tampilkan kamera hanya jika status ON
                if st.session_state[cam_key]:
                    qr_cam_img = st.camera_input("Arahkan kamera ke QR Code", key=f"cam_input_{row['id']}")
                    
                    if qr_cam_img:
                        qr = scan_qr_from_image(Image.open(qr_cam_img))
                        if qr:
                            st.success(f"QR Terdeteksi: {qr}")
                            qr_input = qr
                        else:
                            st.error("QR tidak terbaca. Coba ulangi.")
                            
                # ================================
                # 📸 Upload bukti foto pembuangan
                # ================================
                st.markdown("#### 📸 Upload Foto Bukti Pembuangan")
                proof_image = st.file_uploader(
                    "Upload foto",
                    type=['jpg', 'jpeg', 'png'],
                    key=f"proof_{row['id']}"
                )
                
                if proof_image and qr_input:
                    st.image(proof_image, caption="Foto Bukti", use_container_width=True)
                    
                    if st.button(f"✅ Konfirmasi Pembuangan", key=f"confirm_{row['id']}", type="primary"):
                        img_bytes = image_to_bytes(Image.open(proof_image))
                        
                        db.create_disposal(user['id'], row['id'], qr_input, img_bytes)
                        db.update_detection_status(row['id'], 'disposed')
                        db.update_user_points(user['id'], row['points'])
                        
                        st.success(f"🎉 Berhasil! Poin didapat: {row['points']}")
                        st.balloons()
                        st.rerun()

            with col2:
                st.write("")   # kosong 