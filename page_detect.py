import streamlit as st
from PIL import Image
from datetime import datetime
from config import Config
from image_processor import image_to_bytes

def render_detect_page(db, user, detector):
    st.markdown('<div style="font-size: 3rem; font-weight: bold; color: #2E7D32; text-align: center; padding: 1rem; background: linear-gradient(135deg, #81C784 0%, #4CAF50 100%); border-radius: 10px; margin-bottom: 2rem;">📸 Deteksi Sampah</div>', unsafe_allow_html=True)
    
    if st.button("← Kembali ke Home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("### Upload atau Ambil Foto Sampah")
    st.info("💡 Arahkan kamera ke sampah plastik untuk mendeteksinya. Anda punya 24 jam untuk membuangnya!")
    
    option = st.radio("Pilih metode:", ["📤 Upload Gambar", "📷 Gunakan Kamera"])
    
    image = None
    
    if option == "📤 Upload Gambar":
        uploaded_file = st.file_uploader("Upload foto sampah", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            try:
                image = Image.open(uploaded_file).convert("RGB")
            except:
                st.error("Gagal membaca gambar.")
                return
    else:
        camera_image = st.camera_input("Ambil foto sampah")
        if camera_image:
            try:
                image = Image.open(camera_image).convert("RGB")
            except:
                st.error("Gagal membaca gambar kamera.")
                return
    
    if image:
        col1, col2 = st.columns(2)
        
        # Tampilkan gambar asli
        with col1:
            st.image(image, caption="Foto Original", use_container_width=True)
        
        # Jalankan deteksi
        with col2:
            with st.spinner("🔍 Mendeteksi sampah..."):
                detections, annotated = detector.detect(image)
                st.image(annotated, caption="Hasil Deteksi", use_container_width=True)
        
        # Jika terdeteksi
        if detections:
            st.success(f"✅ Terdeteksi {len(detections)} item sampah!")
            
            total_points = 0
            for det in detections:
                waste_class = det['class'].lower()
                points = detector.calculate_points(waste_class)
                total_points += points
                confidence = det.get('confidence', 0.9)
                
                st.write(
                    f"- **{waste_class.title()}** "
                    f"(Confidence: {confidence:.2%}) → {points} poin"
                )
            
            st.markdown(f"### 🎁 Total Poin: **{total_points}**")
            st.warning("⚠️ Poin akan hangus dalam 24 jam jika tidak segera dibuang!")
            
            if st.button("💾 Simpan Deteksi", type="primary"):
                image_bytes = image_to_bytes(image)
                expires_at = datetime.now() + Config.get_expiry_timedelta()
                
                for det in detections:
                    waste_class = det['class']
                    points = detector.calculate_points(waste_class)
                    
                    db.create_detection(
                        user['id'],
                        waste_class,
                        points,
                        image_bytes,
                        expires_at
                    )
                
                st.success("✅ Deteksi berhasil disimpan! Jangan lupa buang dalam 24 jam.")
                st.balloons()
        else:
            st.error("❌ Tidak ada sampah terdeteksi. Coba foto yang lebih jelas!")