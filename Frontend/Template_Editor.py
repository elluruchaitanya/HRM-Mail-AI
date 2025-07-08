import streamlit as st

def template_editor_page():
    st.title("📝 Template Editor")
    st.markdown("Write or edit your template content below.")

    template_text = st.text_area("Template Content", height=300, placeholder="Write your template here...")

    if st.button("Save Template"):
        st.success("✅ Template saved successfully!")
        st.write("### 📄 Current Template:")
        st.code(template_text)
