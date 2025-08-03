import streamlit as st
from streamlit_chat import message
import httpx

API_URL = "http://localhost:8000/chat/stream"

st.set_page_config(page_title="AI Chatbot (LM Studio)", page_icon="🤖", layout="centered")
st.title("🤖 AI Chatbot (LM Studio)")

if "history" not in st.session_state:
    st.session_state["history"] = []

user_input = st.text_input("You:", key="input", placeholder="Type your message and press Enter...")
send_btn = st.button("Send")

if send_btn and user_input.strip():
    # Prepare message history excluding current input (it will be sent as the latest user input)
    placeholder = st.empty()
    bot_reply = ""

    with st.spinner("AI is thinking..."):
        try:
            # NOTE: Send history without the current user message.
            with httpx.stream("POST", API_URL, json={
                "message": user_input,
                "history": st.session_state["history"]
            }, timeout=60.0) as r:
                for chunk in r.iter_text():
                    bot_reply += chunk
                    placeholder.markdown(f"🤖 **AI:** {bot_reply}▌")

        except Exception as e:
            bot_reply = f"⚠️ Error: {e}"
            st.error(bot_reply)

    # Now update history: add user input and then bot reply
    st.session_state["history"].append({"role": "user", "content": user_input})
    st.session_state["history"].append({"role": "assistant", "content": bot_reply})

    st.rerun()  # Refresh after new message

# Display chat history on screen
for i, msg in enumerate(st.session_state["history"]):
    is_user = msg["role"] == "user"
    message(msg["content"], is_user=is_user, key=str(i))
