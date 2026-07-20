from typing import List, Tuple
from app.schemas import DiscoverySessionState

# قائمة بالمحاور الأساسية للمقابلة بالترتيب حسب الـ Survey
DISCOVERY_TOPICS = [
    "About You",
    "Department Performance & KPIs",
    "Key Workflows & Pain Points",
    "Systems & Data Landscape",
    "Governance & Adoption",
    "Completed"
]

class TopicTracker:
    def __init__(self):
        self.topics = DISCOVERY_TOPICS

    def get_next_topic(self, current_topic: str) -> str:
        """يرجع الموضوع التالي بناءً على الموضوع الحالي"""
        try:
            current_index = self.topics.index(current_topic)
            if current_index + 1 < len(self.topics):
                return self.topics[current_index + 1]
            return "Completed"
        except ValueError:
            return self.topics[0]

    def update_state_progress(self, state: DiscoverySessionState, user_input: str) -> DiscoverySessionState:
        """
        يفحص حالة البيانات الحالية ويحدد إذا اكتفينا من الموضوع الحالي للنقل للي بعده
        """
        curr = state.current_topic

        # شروط بسيطة للنقل بين المحاور (تستند لحضور البيانات الأساسية)
        if curr == "About You" and state.role_info.role_title:
            if "About You" not in state.completed_topics:
                state.completed_topics.append("About You")
            state.current_topic = "Department Performance & KPIs"

        elif curr == "Department Performance & KPIs" and state.kpis.tracked_kpis:
            if "Department Performance & KPIs" not in state.completed_topics:
                state.completed_topics.append("Department Performance & KPIs")
            state.current_topic = "Key Workflows & Pain Points"

        elif curr == "Key Workflows & Pain Points" and state.primary_workflow.process_name:
            if "Key Workflows & Pain Points" not in state.completed_topics:
                state.completed_topics.append("Key Workflows & Pain Points")
            state.current_topic = "Systems & Data Landscape"

        elif curr == "Systems & Data Landscape" and state.primary_workflow.systems_used:
            if "Systems & Data Landscape" not in state.completed_topics:
                state.completed_topics.append("Systems & Data Landscape")
            state.current_topic = "Governance & Adoption"

        elif curr == "Governance & Adoption" and len(state.completed_topics) >= 4:
            if "Governance & Adoption" not in state.completed_topics:
                state.completed_topics.append("Governance & Adoption")
            state.current_topic = "Completed"

        return state