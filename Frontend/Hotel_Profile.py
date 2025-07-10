import streamlit as st
from mongo_helper import insert_or_update_hotel_profile, get_hotel_profile_by_id, get_all_hotel_ids

def hotel_profile_page():
    st.title("Hotel Profile Form")

    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "hotel_id": "",
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
                "manager_name": existing.get("manager_name", ""),
                "stop_words": ", ".join(existing.get("stop_words", [])),
                "usps": ", ".join(existing.get("usps", [])),
                "reference_urls": ", ".join(existing.get("reference_urls", [])),
            }

    form_data = st.session_state.form_data

    with st.form("hotel_profile_form", clear_on_submit=False):
        manager_name = st.text_input("Manager Name", max_chars=150, value=form_data["manager_name"])
        stop_words = st.text_area("Stop Words (comma-separated)", max_chars=1000, value=form_data["stop_words"])
        usps = st.text_area("USPs (comma-separated)", max_chars=1000, value=form_data["usps"])
        reference_urls = st.text_area("Reference URLs (comma-separated)", max_chars=1000, value=form_data["reference_urls"])

        submitted = st.form_submit_button("✅ Submit")

        if submitted:
            if not hotel_id.strip() or not manager_name.strip():
                st.error("Hotel ID and Manager Name are required.")
            else:
                data = {
                    "hotel_id": hotel_id.strip(),
                    "manager_name": manager_name.strip(),
                    "stop_words": [w.strip() for w in stop_words.split(",") if w.strip()],
                    "usps": [u.strip() for u in usps.split(",") if u.strip()],
                    "reference_urls": [r.strip() for r in reference_urls.split(",") if r.strip()],
                }
                result = insert_or_update_hotel_profile(data)
                #read the basic template
                #replace the holders with data properties
                #save as new file with the name hotelid.txt

                if result == "Updated":
                    st.success("✅ Profile updated successfully!")
                else:
                    st.success(f"✅ New profile created! ID: {result}")

                st.session_state.form_data = {
                    "hotel_id": "",
                    "manager_name": "",
                    "stop_words": "",
                    "usps": "",
                    "reference_urls": ""
                }
