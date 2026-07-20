import os
import json
import ollama
from app.schemas import DiscoverySessionState

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

class DiscoveryAgent:
    def __init__(self):
        self.model = OLLAMA_MODEL

    def generate_response(self, state: DiscoverySessionState, chat_history: list) -> str:
        system_prompt = f"""
You are an expert AI Discovery Consultant at CogniVerse conducting a discovery interview with a department lead at an automotive dealership.

Context & Rules:
- Current Topic/Section: {state.current_topic}
- Completed Topics: {', '.join(state.completed_topics) if state.completed_topics else 'None'}
- Goal: Ask natural, insightful follow-up questions to understand their pain points, KPIs, workflows, and system challenges.
- DO NOT sound like a rigid survey or read questions verbatim.
- Keep it conversational (1-2 clear questions at a time).
- Acknowledge their previous answer briefly before asking the next question.
- If the current topic is 'Completed', thank them and wrap up the discovery session professionally.
        """

        messages = [{"role": "system", "content": system_prompt}]

        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def extract_structured_data(self, state: DiscoverySessionState, user_input: str) -> dict:
        extraction_prompt = f"""
Analyze this user statement from an interview and extract key facts.

User Input: "{user_input}"

Extract into a simple JSON with EXACTLY these keys (if not present, use null or empty list []):
{{
  "role_title": string or null,
  "tracked_kpis": list of strings,
  "process_name": string or null,
  "time_consumed": string or null,
  "systems_used": list of strings,
  "workarounds": list of strings
}}

Return ONLY valid raw JSON. No markdown codeblocks, no explanations.
"""

        try:
            res = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                format="json"  # إجبار Ollama على إرجاع JSON صريح
            )
            content = res['message']['content'].strip()
            return json.loads(content)
        except Exception:
            return {}