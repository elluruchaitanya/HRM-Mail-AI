import streamlit as st
import os
import datetime
from pathlib import Path

template_directory=Path(__file__).parent / "HotelTemplates"
def get_templates():
    files = sorted(os.listdir(template_directory), reverse=True)
    return [f for f in files if f.endswith(".txt")]


def template_editor_page():
    st.title("📝 Prompt Rules Editor")
    st.markdown("Write or edit your template content below.")
    st.subheader("📂 Load Existing Hotel Prompts")
    templates = get_templates()
    selected_version = st.selectbox("Choose a Prompt Rule to load", [""] + templates)

    if selected_version:
        with open(os.path.join(template_directory, selected_version), "r", encoding="utf-8") as f:
            content = f.read()
        st.session_state["text"] = content
        st.session_state["filename"] = selected_version
        #st.info(f"Loaded version: {selected_version}")

    # Text editor
    if "text" in st.session_state:
        st.subheader("✏️ Edit Rules")
        updated_text = st.text_area("Update rules below:", value=st.session_state["text"], height=300)

        if st.button("💾 Save"):
            #filename = save_new_version(updated_text, st.session_state.get("filename", "edited"))
            #st.success(f"Saved successfully as `{filename}`")
            st.session_state["text"] = updated_text  # Update with new edits
            path = os.path.join(template_directory, st.session_state.get("filename"))
            print(f"path of the file",path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated_text)
        #template_text = st.text_area("Template Content", height=300, placeholder="Write your template here...")

        # if st.button("Save Template"):
        #     st.success("✅ Template saved successfully!")
        #     st.write("### 📄 Current Template:")
        #     st.code(template_text)
