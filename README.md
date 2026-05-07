# TalentScout Hiring Assistant 🤖

## I. Project Overview
The **TalentScout Hiring Assistant** is a high-performance AI chatbot designed for "TalentScout," a recruitment agency. It automates the initial candidate screening process by gathering details, analyzing sentiment, and conducting technical interviews in multiple languages.

### Key Features:
- **Dynamic Screening**: Sequential gathering of Name, Contact, Experience, and Tech Stack.
- **2026 Tech Stack Assessment**: Generates 3-5 tailored technical questions using cutting-edge models.
- **Multilingual Support**: Conducts interviews in English, Spanish, French, German, Hindi, and Telugu.
- **Sentiment Analysis**: Real-time monitoring of candidate emotions (😊, 😐, 😟).
- **Premium WhatsApp UI**: Dark-mode interface with left/right bubble alignment.
- **Optimized Performance**: Low-latency response logic with verified model persistence.

---

## II. Installation Instructions

### Prerequisites:
- Python 3.9+
- Google Gemini API Key

### Steps:
1. **Prepare Directory**: `cd "TalentScout Hiring Assistant"`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure API**: Create a `.env` file with `GEMINI_API_KEY=your_key`.
4. **Run App**: `streamlit run app.py`

---

## III. Technical Details

### Model & SDK:
- **Core Engine**: Google **Gemini 2.5 Flash** & **Gemma 4 (2026 Series)**.
- **SDK**: Unified `google-genai` SDK.
- **Performance**: Implemented **Stage-Conditional Extraction** to reduce LLM overhead by 50% during technical questioning.

### Architectural Decisions:
- **State Machine**: Custom stage-based logic for structured data collection.
- **Model Persistence**: Dynamically identifies the best working model on your account and locks it for the duration of the session to eliminate retry latency.
- **GDPR Compliance**: Ephemeral, session-only storage with no persistent PII logging.

---

## IV. Deployment (Streamlit Cloud)
To deploy this app on **Streamlit Community Cloud**:
1. Push your repository to GitHub (ensure `.env` is **not** pushed).
2. Connect your repo to [Streamlit Cloud](https://share.streamlit.io/).
3. In the app settings, go to **Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

---

## IV. Prompt Design
- **Extraction (Pass 1)**: Converts natural language into structured JSON.
- **Conversation (Pass 2)**: Uses a stage-specific System Prompt to maintain persona and objective.
- **Technical Generation**: Tailored questioning based on the specific versions of technologies declared by the candidate.

---

## V. Challenges & Solutions (2026 Edition)
- **Model Availability**: Resolved 404 errors caused by legacy model deprecation (v1.5) by implementing a discovery layer for 2026 model variants.
- **Latency Management**: Optimized the response time by eliminating redundant LLM calls during the non-gathering stages.
- **Interface Alignment**: Solved Streamlit's alignment limitations using custom CSS for a WhatsApp-style experience.

---

### Developed for the AI/ML Intern Assignment - TalentScout.
