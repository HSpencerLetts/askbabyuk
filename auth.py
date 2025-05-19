import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def show_login():
    """Displays login or signup form and stores session state."""
    st.subheader("🔐 Login to AskBaby.uk")

    auth_mode = st.radio("Choose an option:", ["Login", "Sign up"], horizontal=True)
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter a password")

    if st.button("Continue"):
        if auth_mode == "Login":
            session = login(email, password)
        else:
            session = signup(email, password)

        if session:
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Authentication failed.")


def login(email, password):
    """Logs in user and saves session tokens."""
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if result.user:
            st.session_state["user"] = result.user
            st.session_state["access_token"] = result.session.access_token
            st.session_state["refresh_token"] = result.session.refresh_token
            return result.session
    except Exception as e:
        st.error(f"Login failed: {e}")
    return None


def signup(email, password):
    """Signs up user and saves session tokens."""
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if result.user:
            st.session_state["user"] = result.user
            st.session_state["access_token"] = result.session.access_token
            st.session_state["refresh_token"] = result.session.refresh_token
            return result.session
    except Exception as e:
        st.error(f"Signup failed: {e}")
    return None


def get_user():
    """Returns logged-in user, or tries to restore session from token."""
    if "user" in st.session_state:
        return st.session_state.user

    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    if access_token and refresh_token:
        try:
            session = supabase.auth.refresh_session(refresh_token)
            if session and session.user:
                st.session_state.user = session.user
                st.session_state.access_token = session.access_token
                st.session_state.refresh_token = session.refresh_token
                return session.user
        except Exception as e:
            st.warning("Session expired. Please log in again.")
            st.session_state.pop("access_token", None)
            st.session_state.pop("refresh_token", None)

    return None
