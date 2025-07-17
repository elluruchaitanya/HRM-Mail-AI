import streamlit as st
from Hotel_Profile import hotel_profile_page
from Template_Editor import template_editor_page
from pathlib import Path

st.set_page_config(page_title="Arissa AI", layout="wide", initial_sidebar_state="expanded",page_icon="assets/favicon.ico",)

def load_css(file_name):
    css_path = Path(__file__).parent / file_name
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("main.css")
sidebarlogo = "assets/Website 4.svg"

# Navigation logic
if "current_page" not in st.session_state:
    st.session_state.current_page = "Hotel Profile"

# Sidebar
with st.sidebar:
    st.logo(sidebarlogo)
    if st.button("🏨 Hotel Profile"):
        st.session_state.current_page = "Hotel Profile"
    if st.button("📝 Prompt Rules Editor"):
        st.session_state.current_page = "Template Editor"

# Page routing
if st.session_state.current_page == "Hotel Profile":
    hotel_profile_page()
elif st.session_state.current_page == "Template Editor":
    template_editor_page()
