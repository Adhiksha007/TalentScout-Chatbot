import streamlit as st
import os
from dotenv import load_dotenv
from chatbot_logic import ChatbotLogic

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="TalentScout Hiring Assistant", 
    page_icon="🤖", 
    layout="wide"
)

def load_custom_css():
    """Injects custom WhatsApp-style CSS."""
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def initialize_session_state():
    """Initializes all necessary session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = {
            "Full Name": None,
            "Email Address": None,
            "Phone Number": None,
            "Years of Experience": None,
            "Desired Position": None,
            "Current Location": None,
            "Tech Stack": None
        }
    if "stage" not in st.session_state:
        st.session_state.stage = "GREETING"
    if "tech_questions" not in st.session_state:
        st.session_state.tech_questions = []
    if "current_q_index" not in st.session_state:
        st.session_state.current_q_index = 0
    if "language" not in st.session_state:
        st.session_state.language = "English"
    if "sentiment" not in st.session_state:
        st.session_state.sentiment = "Neutral"
    if "working_model" not in st.session_state:
        st.session_state.working_model = None

# --- MAIN EXECUTION ---

load_custom_css()
initialize_session_state()

# API Key handling logic
# Prioritizes Streamlit Secrets (Cloud) -> .env (Local) -> Manual Input
api_key = os.getenv("GEMINI_API_KEY")

if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# Sidebar Implementation
with st.sidebar:
    st.title("TalentScout")
    
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    
    # BONUS: Multilingual Support
    st.session_state.language = st.selectbox(
        "Interview Language", 
        ["English", "Spanish", "French", "German", "Hindi", "Telugu"]
    )
    
    # BONUS: Sentiment Analysis Display
    sentiment_icons = {"Positive": "😊", "Neutral": "😐", "Concerned": "😟"}
    st.markdown(f'<div class="label">Candidate Sentiment</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="value">{sentiment_icons.get(st.session_state.sentiment, "😐")} {st.session_state.sentiment}</div>', unsafe_allow_html=True)
    
    st.subheader("Candidate Profile")
    for key, value in st.session_state.candidate_data.items():
        st.markdown(f'<div class="label">{key}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="value">{value if value else "Pending..."}</div>', unsafe_allow_html=True)
    
    if st.button("Reset Conversation"):
        for key in ["messages", "candidate_data", "stage", "tech_questions", "current_q_index", "sentiment", "working_model"]:
            if key == "messages": st.session_state[key] = []
            elif key == "candidate_data": st.session_state[key] = {k: None for k in st.session_state.candidate_data}
            elif key == "stage": st.session_state[key] = "GREETING"
            elif key == "sentiment": st.session_state[key] = "Neutral"
            elif key == "working_model": st.session_state[key] = None
            else: st.session_state[key] = 0 if key == "current_q_index" else []
        st.rerun()
    
    if st.button("Test API Connection"):
        if not api_key:
            st.error("Please provide an API Key first.")
        else:
            with st.status("🔍 Checking API connection...", expanded=True) as status:
                st.write("Verifying credentials...")
                test_chatbot = ChatbotLogic(api_key)
                st.write("Identifying available models...")
                success, model_name, error = test_chatbot.test_connection()
                
                if success:
                    st.session_state.working_model = model_name # Store verified model
                    status.update(label=f"✅ Connected to {model_name}!", state="complete", expanded=False)
                    st.success(f"Success! Chat will now use **{model_name}**.")
                else:
                    status.update(label="❌ Connection failed", state="error", expanded=True)
                    st.error(f"Error: {error}")

# Main UI
st.title("🤖 TalentScout Hiring Assistant")
st.write(f"Welcome. The interview will proceed in **{st.session_state.language}**.")

if not api_key:
    st.warning("Please provide a Gemini API Key to start the conversation.")
    st.stop()

chatbot = ChatbotLogic(api_key)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    initial_response = chatbot.handle_conversation(st.session_state, "")
    st.session_state.messages.append({"role": "assistant", "content": initial_response})
    st.rerun()

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        response = chatbot.handle_conversation(st.session_state, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
