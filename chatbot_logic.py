import os
import json
from google import genai
from prompts import SYSTEM_PROMPT, INFO_EXTRACTION_PROMPT, TECH_QUESTION_PROMPT, FALLBACK_PROMPT, STAGE_OBJECTIVES

class ChatbotLogic:
    """
    Core logic for the TalentScout Hiring Assistant.
    Optimized for low-latency response times.
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        
    def test_connection(self):
        """Diagnostic method to verify API and identify the best model."""
        try:
            available_models = []
            for m in self.client.models.list():
                if "generateContent" in m.supported_actions:
                    name = m.name.split('/')[-1] if '/' in m.name else m.name
                    available_models.append(name)
            
            preferred_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemma-4-26b-a4b-it"]
            models_to_check = [m for m in preferred_models if m in available_models] + [m for m in available_models if m not in preferred_models]
            
            for model_name in models_to_check:
                try:
                    self.client.models.generate_content(model=model_name, contents="test")
                    return True, model_name, None
                except:
                    continue
            return False, None, "No responding models found."
        except Exception as e:
            return False, None, str(e)

    def get_completion(self, prompt, preferred_model=None):
        """Single-shot inference using the verified model to reduce latency."""
        # Use the verified model if available, otherwise default to a high-speed one
        model_name = preferred_model if preferred_model else "gemini-2.5-flash"
        try:
            response = self.client.models.generate_content(model=model_name, contents=prompt)
            return response.text
        except:
            # Fallback only if the primary fails
            fallbacks = ["gemini-2.0-flash", "gemma-4-26b-a4b-it"]
            for fb in fallbacks:
                if fb != model_name:
                    try:
                        resp = self.client.models.generate_content(model=fb, contents=prompt)
                        return resp.text
                    except:
                        continue
        return "Error: Model connection lost."

    def extract_info(self, user_input, preferred_model=None):
        """Extracts info only when necessary."""
        prompt = INFO_EXTRACTION_PROMPT.format(user_input=user_input)
        response = self.get_completion(prompt, preferred_model)
        try:
            clean_response = response.strip().replace('```json', '').replace('```', '')
            return json.loads(clean_response)
        except:
            return {}

    def generate_tech_questions(self, tech_stack, preferred_model=None):
        prompt = TECH_QUESTION_PROMPT.format(tech_stack=tech_stack)
        response = self.get_completion(prompt, preferred_model)
        questions = [q.strip() for q in response.split('\n') if q.strip() and (q.strip()[0].isdigit() or q.strip().startswith('-'))]
        return questions[:5]

    def get_contextual_response(self, session_state, user_input, objective):
        preferred_model = session_state.get("working_model")
        system_msg = SYSTEM_PROMPT.format(
            name=session_state.candidate_data.get("Full Name", "Candidate"),
            stage=session_state.stage,
            tech_stack=session_state.candidate_data.get("Tech Stack", "Not specified yet"),
            language=session_state.get("language", "English"),
            objective=objective
        )
        history = ""
        for msg in session_state.messages[-4:]:
            history += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
        full_prompt = f"{system_msg}\n\nChat History:\n{history}\nUser: {user_input}\nAssistant:"
        return self.get_completion(full_prompt, preferred_model)

    def handle_conversation(self, session_state, user_input):
        preferred_model = session_state.get("working_model")
        
        # 1. Exit early if requested
        if any(word in user_input.lower() for word in ["exit", "quit", "bye", "terminate"]):
            session_state.stage = "COMPLETED"
            return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["EXIT"])

        # 2. OPTIMIZATION: Only run extraction during info-gathering stages
        gathering_stages = ["COLLECT_BASIC_INFO", "COLLECT_CONTACT_EXP", "COLLECT_TECH_STACK", "COLLECT_LOCATION"]
        if session_state.stage in gathering_stages:
            new_info = self.extract_info(user_input, preferred_model)
            if "Sentiment" in new_info:
                session_state.sentiment = new_info["Sentiment"]
            for key, value in new_info.items():
                if key != "Sentiment" and value and not session_state.candidate_data.get(key):
                    session_state.candidate_data[key] = value

        # 3. State Machine Logic
        if session_state.stage == "GREETING":
            session_state.stage = "COLLECT_BASIC_INFO"
            return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["GREETING"])

        elif session_state.stage == "COLLECT_BASIC_INFO":
            if session_state.candidate_data["Full Name"] and session_state.candidate_data["Desired Position"]:
                session_state.stage = "COLLECT_CONTACT_EXP"
                return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["COLLECT_BASIC_INFO"])
            return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["FALLBACK_BASIC"])

        elif session_state.stage == "COLLECT_CONTACT_EXP":
            if session_state.candidate_data["Email Address"] and session_state.candidate_data["Phone Number"] and session_state.candidate_data["Years of Experience"]:
                session_state.stage = "COLLECT_TECH_STACK"
                return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["COLLECT_CONTACT_EXP"])
            return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["FALLBACK_CONTACT"])

        elif session_state.stage == "COLLECT_TECH_STACK":
            if session_state.candidate_data["Tech Stack"]:
                session_state.stage = "TECH_QUESTIONING"
                session_state.tech_questions = self.generate_tech_questions(session_state.candidate_data["Tech Stack"], preferred_model)
                session_state.current_q_index = 0
                obj = STAGE_OBJECTIVES["COLLECT_TECH_STACK"].format(question=session_state.tech_questions[0])
                return self.get_contextual_response(session_state, user_input, obj)
            return self.get_contextual_response(session_state, user_input, "Politely request the candidate's tech stack.")

        elif session_state.stage == "TECH_QUESTIONING":
            session_state.current_q_index += 1
            if session_state.current_q_index < len(session_state.tech_questions):
                obj = STAGE_OBJECTIVES["TECH_QUESTIONING"].format(question=session_state.tech_questions[session_state.current_q_index])
                return self.get_contextual_response(session_state, user_input, obj)
            else:
                session_state.stage = "COLLECT_LOCATION"
                return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["COLLECT_LOCATION"])

        elif session_state.stage == "COLLECT_LOCATION":
            if session_state.candidate_data["Current Location"]:
                session_state.stage = "COMPLETED"
                return self.get_contextual_response(session_state, user_input, STAGE_OBJECTIVES["COMPLETED"])
            return self.get_contextual_response(session_state, user_input, "Politely ask for their current location.")

        else:
            return "Interview complete. Type 'exit' to end."
