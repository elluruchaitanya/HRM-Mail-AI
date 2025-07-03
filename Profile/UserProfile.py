import streamlit as st
import os
import datetime

# Directory to store versioned text files
VERSION_DIR = "versions"
os.makedirs(VERSION_DIR, exist_ok=True)

st.set_page_config(page_title="Text Editor with Versioning", layout="centered")
st.title("📝 Text File Editor with Versioning")

# Get list of existing versions
def get_version_list():
    files = sorted(os.listdir(VERSION_DIR), reverse=True)
    return [f for f in files if f.endswith(".txt")]

# Save new version
def save_new_version(content, base_name="uploaded"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_v{timestamp}.txt"
    path = os.path.join(VERSION_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# Upload mode
st.subheader("📤 Upload New Text File")
uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    base_name = os.path.splitext(uploaded_file.name)[0]
    st.session_state["text"] = content
    st.session_state["filename"] = base_name
    st.success(f"Loaded: {uploaded_file.name}")

# Load from existing version
st.subheader("📂 Load Existing Version")
versions = get_version_list()
selected_version = st.selectbox("Choose a version to load", [""] + versions)

if selected_version:
    with open(os.path.join(VERSION_DIR, selected_version), "r", encoding="utf-8") as f:
        content = f.read()
    st.session_state["text"] = content
    st.session_state["filename"] = selected_version.rsplit("_v", 1)[0]
    st.info(f"Loaded version: {selected_version}")

# Text editor
if "text" in st.session_state:
    st.subheader("✏️ Edit Content")
    updated_text = st.text_area("Edit your text below:", value=st.session_state["text"], height=300)

    if st.button("💾 Save as New Version"):
        filename = save_new_version(updated_text, st.session_state.get("filename", "edited"))
        st.success(f"Saved successfully as `{filename}`")
        st.session_state["text"] = updated_text  # Update with new edits