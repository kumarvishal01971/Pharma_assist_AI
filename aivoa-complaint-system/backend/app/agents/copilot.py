import json
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.graph import reasoning_llm
from app.agents.prompts import COPILOT_SYSTEM_PROMPT


def answer_copilot_question(message: str, complaint_context: dict | None) -> str:
    context_str = json.dumps(complaint_context) if complaint_context else "No complaint loaded yet."
    response = reasoning_llm.invoke([
        SystemMessage(content=COPILOT_SYSTEM_PROMPT),
        HumanMessage(content=f"Complaint data:\n{context_str}\n\nQuestion: {message}"),
    ])
    return response.content.strip()
