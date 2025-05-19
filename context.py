import streamlit as st
from datetime import datetime
from db import get_profile, save_profile, update_profile  # ✅ include update

def collect_user_context():
    user = st.session_state.get("user")
    if not user:
        st.error("User not authenticated.")
        return

    is_updating = st.session_state.get("update_mode", False)

    # Check for saved profile
    profile = get_profile(user.id)

    if profile and not is_updating:
        # Load saved values into session state
        st.session_state.parent_name = profile.get("parent_name", "Parent")
        st.session_state.baby_name = profile.get("baby_name", "your baby")

        dob_str = profile.get("baby_dob")
        st.session_state.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        # Calculate baby's age in weeks
        today = datetime.today().date()
        age_days = (today - st.session_state.dob).days
        st.session_state.baby_age_weeks = age_days // 7

        st.session_state.context_set = True
        st.success(f"Welcome back, {st.session_state.parent_name}! Baby info loaded.")

    else:
        # Show form (either new profile or update mode)
        st.subheader("🍼 Update Baby Details" if is_updating else "🍼 Tell us about your baby")

        with st.form("context_form"):
            parent_name = st.text_input("Your name (optional)", value=st.session_state.get("parent_name", ""), placeholder="e.g. Alex")
            baby_name = st.text_input("Baby's name", value=st.session_state.get("baby_name", "Ellie"), placeholder="e.g. Ellie 👶")
            dob = st.date_input("Baby's date of birth", value=st.session_state.get("dob"))

            submitted = st.form_submit_button("Save and Continue")

            if submitted:
                st.session_state.parent_name = parent_name or "Parent"
                st.session_state.baby_name = baby_name or "your baby"
                st.session_state.dob = dob
                st.session_state.baby_age_weeks = (datetime.today().date() - dob).days // 7
                st.session_state.context_set = True
                st.session_state.update_mode = False

                if is_updating:
                    update_profile(user.id, parent_name, baby_name, dob.isoformat())
                else:
                    save_profile(user.id, parent_name, baby_name, dob.isoformat())

                st.success("Profile saved! You're all set.")
                st.rerun()
