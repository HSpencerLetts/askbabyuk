import streamlit as st
from chat import get_ellie_response
from context import collect_user_context
from prompts import build_system_prompt
from auth import show_login, get_user
from db import (
    save_message,
    get_user_messages,
    save_profile,
    export_user_messages_csv,
    save_feedback,
    get_all_messages,
    get_all_feedback,
)
from PIL import Image
import os
import pandas as pd

st.set_page_config(page_title="AskBaby.uk", page_icon="👶", layout="centered")

# --- Logo ---
logo_path = os.path.join("static", "logo.png")
logo = Image.open(logo_path)
st.image(logo, width=150)

# --- Auth ---
user = get_user()
if not user:
    show_login()
    st.stop()

# --- Admin Access ---
ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "")
is_admin = user.email.lower() == ADMIN_EMAIL.lower()


# --- Session State ---
if "context_set" not in st.session_state:
    st.session_state.context_set = False
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# --- Load Profile ---
if not st.session_state.context_set:
    collect_user_context()

# --- Title & Intro ---
st.title("👶 AskBaby.uk – Ask Ellie")
st.markdown("_Your gentle AI guide for new UK parents. Powered by NHS-based information._")
st.markdown("**⚠️ Disclaimer:** This is not medical advice. If in doubt, contact your GP or call NHS 111.")

# --- Sidebar Profile ---
st.sidebar.title("👶 My Baby Profile")
st.sidebar.markdown(f"**Logged in as:** {user.email}")
st.sidebar.markdown(f"**Admin access:** {'✅' if is_admin else '❌'}")

if "baby_name" in st.session_state and "dob" in st.session_state:
    st.sidebar.markdown(f"**Name:** {st.session_state.baby_name}")
    st.sidebar.markdown(f"**DOB:** {st.session_state.dob}")
    st.sidebar.markdown(f"**Age:** {st.session_state.baby_age_weeks} weeks")

    if st.sidebar.button("✏️ Update Baby Info"):
        st.session_state.context_set = False
        st.session_state.update_mode = True
        st.rerun()

else:
    st.sidebar.info("Baby info will appear here after you complete the form.")

# --- Tabs ---
if is_admin:
    tab1, tab2, tab3 = st.tabs(["🧠 Chat with Ellie", "📜 Past Chats", "🛠 Admin Dashboard"])
else:
    tab1, tab2 = st.tabs(["🧠 Chat with Ellie", "📜 Past Chats"])

# --- Tab 1: Chat ---
with tab1:
    if st.session_state.context_set:
        st.markdown("---")
        st.subheader(f"💬 Ask Ellie about {st.session_state.baby_name}")

        # ✅ Clear Chat Button
        st.button("🧹 Start New Chat", on_click=lambda: (
            st.session_state.history.clear(),
            st.session_state.__setitem__("chat_input", ""),
            st.session_state.__setitem__("last_input", "")
        ))

        # Input box
        st.session_state.chat_input = st.text_input(
            f"Ask a question about {st.session_state.baby_name}",
            value=st.session_state.get("chat_input", ""),
            key="chat_input_box"
        )

        # Submit button
        if st.button("Send"):
            user_input = st.session_state.chat_input.strip()

            if user_input:
                st.session_state.last_input = user_input
                st.session_state.history.append({"role": "user", "content": user_input})

                try:
                    with st.spinner("🤖 Ellie is thinking..."):
                        system_prompt = build_system_prompt()
                        reply = get_ellie_response(system_prompt, st.session_state.history)

                    st.session_state.history.append({"role": "assistant", "content": reply})
                    save_message(user.id, user_input, reply)
                except Exception as e:
                    reply = f"❌ Error: {e}"
                    st.session_state.history.append({"role": "assistant", "content": reply})

                st.session_state.chat_input = ""
                st.rerun()

        # Chat history for this session
        for i, msg in enumerate(st.session_state.history):
            if msg["role"] == "user":
                st.markdown(f"👤 **You:** {msg['content']}")
            else:
                st.markdown(f"🤖 **Ellie:** {msg['content']}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"👍 Helpful #{i}"):
                        save_feedback(user.id, st.session_state.history[i - 1]["content"], msg["content"], "thumbs_up")
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button(f"👎 Not helpful #{i}"):
                        save_feedback(user.id, st.session_state.history[i - 1]["content"], msg["content"], "thumbs_down")
                        st.info("We'll keep improving Ellie.")

# --- Tab 2: Past Chats ---
with tab2:
    st.subheader("📜 Your Past Questions")

    csv = export_user_messages_csv(user.id)
    if csv:
        st.download_button(
            label="⬇️ Download chat history as CSV",
            data=csv,
            file_name="askbaby_chat_history.csv",
            mime="text/csv",
        )

    past_messages = get_user_messages(user.id)

    if not past_messages:
        st.info("You haven’t asked Ellie anything yet.")
    else:
        for msg in past_messages:
            st.markdown(f"**🕒 {msg['timestamp']}**")
            st.markdown(f"**👤 You:** {msg['question']}")
            st.markdown(f"**🤖 Ellie:** {msg['answer']}")
            st.markdown("---")

# --- Tab 3: Admin Dashboard ---
if is_admin:
    with tab3:
        st.subheader("🛠 Admin Dashboard")

        st.markdown("### 💬 All Messages")
        messages = get_all_messages()
        if messages:
            df_messages = pd.DataFrame(messages)
            st.dataframe(df_messages)
        else:
            st.info("No messages found.")

        st.markdown("---")
        st.markdown("### 👍👎 Feedback")
        feedback = get_all_feedback()
        if feedback:
            df_feedback = pd.DataFrame(feedback)
            st.dataframe(df_feedback)
        else:
            st.info("No feedback yet.")
