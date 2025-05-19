import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def show_login():
    """Displays login or signup form and stores session state."""
    st.subheader("🔐 Login to AskBaby.uk")

    auth_mode = st.radio("Choose an option:", ["Login", "Sign up"], horizontal=True)
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter a password")

    if st.button("Continue"):
        if auth_mode == "Login":
            user = login(email, password)
        else:
            user = signup(email, password)

        if user:
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Authentication failed.")

def login(email, password):
    """Logs in user using Supabase Auth."""
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state["user"] = result.user
        return result.user
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def signup(email, password):
    """Signs up a new user."""
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.session_state["user"] = result.user
        return result.user
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

def get_user():
    """Returns current logged-in user or None."""
    return st.session_state.get("user", None)
