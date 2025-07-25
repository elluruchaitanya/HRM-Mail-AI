import streamlit as st
import os
from pathlib import Path
from mongo_helper import insert_or_update_hotel_profile, get_hotel_profile_by_id, get_all_hotel_ids

def hotel_profile_page():
    st.title("Hotel Profile")

    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "hotel_id": "",
            "hotel_name": "",  # ✅ Added hotel_name
            "manager_name": "",
            "stop_words": "",
            "usps": "",
            "reference_urls": ""
        }

    all_ids = get_all_hotel_ids()

    # User types hotel ID
    typed_id = st.text_input("Hotel ID", max_chars=10)

    # Show suggestions based on input
    filtered_ids = [hid for hid in all_ids if typed_id.lower() in hid.lower()]

    selected_id = None
    if filtered_ids and typed_id:
        selected_id = st.selectbox("🔍 Suggestions", filtered_ids)

    # Prefer suggestion if selected, else use typed
    hotel_id = selected_id or typed_id

    # Auto-fetch existing
    if hotel_id and hotel_id.strip() != st.session_state.form_data["hotel_id"]:
        existing = get_hotel_profile_by_id(hotel_id.strip())
        if existing:
            st.success("Hotel found. Fields auto-filled.")
            st.session_state.form_data = {
                "hotel_id": existing["hotel_id"],
                "hotel_name": existing.get("hotel_name", ""),  # ✅ Load existing hotel_name
                "manager_name": existing.get("manager_name", ""),
                "stop_words": ", ".join(existing.get("stop_words", [])),
                "usps": ", ".join(existing.get("usps", [])),
                "reference_urls": ", ".join(existing.get("reference_urls", [])),
            }

    form_data = st.session_state.form_data

    with st.form("hotel_profile_form", clear_on_submit=False):
        hotel_name = st.text_input("Hotel Name", max_chars=150, value=form_data["hotel_name"])  # ✅ New field
        manager_name = st.text_input("Manager Name", max_chars=150, value=form_data["manager_name"])
        stop_words = st.text_area("Stop Words (comma-separated)", max_chars=1000, value=form_data["stop_words"])
        usps = st.text_area("USPs (comma-separated)", max_chars=1000, value=form_data["usps"])
        reference_urls = st.text_area("Reference URLs (comma-separated)", max_chars=1000, value=form_data["reference_urls"])

        submitted = st.form_submit_button("✅ Submit")

        if submitted:
            if not hotel_id.strip() or not manager_name.strip() or not hotel_name.strip():
                st.error("Hotel ID, Hotel Name, and Manager Name are required.")
            else:
                data = {
                    "hotel_id": hotel_id.strip(),
                    "hotel_name": hotel_name.strip(),  # ⬅️ Make sure this is in the form
                    "manager_name": manager_name.strip(),
                    "stop_words": [w.strip() for w in stop_words.split(",") if w.strip()],
                    "usps": [u.strip() for u in usps.split(",") if u.strip()],
                    "reference_urls": [r.strip() for r in reference_urls.split(",") if r.strip()],
                }

                # Save/update to DB
                result = insert_or_update_hotel_profile(data)

                if result == "Updated":
                    st.success("✅ Profile updated successfully!")
                else:
                    st.success(f"✅ New profile created! ID: {result}")

                # ✅ Template file generation runs for both create & update
                try:
                    template_path = Path(__file__).parent / "HotelTemplates" / "basic_template.txt"
                    if not template_path.exists():
                        st.warning("⚠️ Template file not found.")
                    else:
                        with open(template_path, "r", encoding="utf-8") as f:
                            template_text = f.read()

                        # Replace placeholders
                        populated = (
                            template_text
                            .replace("{{HOTEL_NAME}}", data["hotel_name"])
                            .replace("{{MANAGER_NAME}}", data["manager_name"])
                            .replace("{{USPS}}", ", ".join(data["usps"]))
                            .replace("{{STOP_WORDS}}", ", ".join(data["stop_words"]))
                            .replace("{{REFERENCE_URLS}}", ", ".join(data["reference_urls"]))
                        )
                        # data["template_content"] = populated

                        # Overwrite or create the file
                        output_file = Path(__file__).parent / "HotelTemplates" / f"{data['hotel_name']}-{data['hotel_id']}.txt"
                        with open(output_file, "w", encoding="utf-8") as out:
                            out.write(populated)

                        st.success(f"📄 Template generated/updated: `{output_file.name}`")

                except Exception as e:
                    st.error(f"❌ Failed to generate/update template: {e}")


                    # Clear form
                    st.session_state.form_data = {
                        "hotel_id": "",
                        "hotel_name": "",
                        "manager_name": "",
                        "stop_words": "",
                        "usps": "",
                        "reference_urls": ""
                    }
