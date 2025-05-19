import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# Use secrets (already loaded)
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def save_message(user_id: str, question: str, answer: str):
    """Save a chat message to the Supabase database."""
    try:
        response = supabase.table("messages").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        return response
    except Exception as e:
        st.error(f"Error saving message to DB: {e}")
        return None

def get_user_messages(user_id: str):
    """Retrieve all messages for the current user, ordered by most recent."""
    try:
        result = (
            supabase
            .table("messages")
            .select("*")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        st.error(f"Error loading past chats: {e}")
        return []

def save_profile(user_id: str, parent_name: str, baby_name: str, dob: str):
    """Insert or update user's baby profile info."""
    try:
        supabase.table("profiles").upsert({
            "user_id": user_id,
            "parent_name": parent_name,
            "baby_name": baby_name,
            "baby_dob": dob
        }).execute()
    except Exception as e:
        st.error(f"Error saving profile: {e}")

def get_profile(user_id: str):
    """Fetch baby info for the logged-in user."""
    try:
        response = (
            supabase.table("profiles")
            .select("parent_name, baby_name, baby_dob")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        return None
    
def export_user_messages_csv(user_id: str):
    """Return a CSV download of a user's past chats."""
    try:
        result = (
            supabase
            .table("messages")
            .select("timestamp, question, answer")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
        data = result.data
        if not data:
            return None

        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')
    except Exception as e:
        st.error(f"Export failed: {e}")
        return None
    

def save_feedback(user_id: str, question: str, answer: str, rating: str):
    """Save feedback (thumbs up/down) for a response."""
    try:
        supabase.table("feedback").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "rating": rating,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")

def get_all_messages():
    try:
        result = (
            supabase.table("messages")
            .select("timestamp, user_id, question, answer")
            .order("timestamp", desc=True)
            .limit(500)
            .execute()
        )
        return result.data
    except Exception as e:
        st.error(f"Error loading messages: {e}")
        return []

def get_all_feedback():
    try:
        result = (
            supabase.table("feedback")
            .select("timestamp, user_id, question, answer, rating")
            .order("timestamp", desc=True)
            .limit(500)
            .execute()
        )
        return result.data
    except Exception as e:
        st.error(f"Error loading feedback: {e}")
        return []

def update_profile(user_id, parent_name, baby_name, baby_dob):
    try:
        supabase.table("profiles").update({
            "parent_name": parent_name,
            "baby_name": baby_name,
            "baby_dob": baby_dob
        }).eq("user_id", user_id).execute()
    except Exception as e:
        st.error(f"Failed to update profile: {e}")
