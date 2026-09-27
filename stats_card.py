import streamlit as st

def render_stats_card(title, value, icon="📊"):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    ">
        <h2>{icon} {value}</h2>
        <p>{title}</p>
    </div>
    """, unsafe_allow_html=True)

def render_feature_card(title, description, emoji):
    st.markdown(f"""
    <div class="feature-card">
        <h3>{emoji} {title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
