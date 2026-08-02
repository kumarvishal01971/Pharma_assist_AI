import json
from typing import TypedDict, Optional, List

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.core.config import settings
from app.agents.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    COMPLETENESS_SYSTEM_PROMPT,
    RISK_CLASSIFICATION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
)


# --- LLM clients ---
# gemma2-9b-it: fast, cheap, good for structured extraction / classification
extraction_llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.extraction_model,
    temperature=0,
)

# llama-3.3-70b-versatile: stronger reasoning, used for risk assessment
reasoning_llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.reasoning_model,
    temperature=0.2,
)


class ComplaintAgentState(TypedDict, total=False):
    raw_text: str
    extracted: dict
    completeness_score: float
    missing_fields: List[str]
    ai_risk_classification: Optional[str]
    ai_risk_rationale: Optional[str]
    ai_summary: Optional[str]
    extraction_confidence: float


def _safe_json_parse(content: str) -> dict:
    """Groq models sometimes wrap JSON in markdown fences despite instructions; strip those."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


# --- Graph nodes ---

def extract_fields_node(state: ComplaintAgentState) -> ComplaintAgentState:
    response = extraction_llm.invoke([
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(content=state["raw_text"]),
    ])
    extracted = _safe_json_parse(response.content)
    # crude confidence heuristic: proportion of non-null fields returned
    non_null = sum(1 for v in extracted.values() if v not in (None, "", "null"))
    confidence = round(non_null / max(len(extracted), 1), 2) if extracted else 0.0
    return {"extracted": extracted, "extraction_confidence": confidence}


def check_completeness_node(state: ComplaintAgentState) -> ComplaintAgentState:
    response = extraction_llm.invoke([
        SystemMessage(content=COMPLETENESS_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(state.get("extracted", {}))),
    ])
    result = _safe_json_parse(response.content)
    return {
        "completeness_score": result.get("completeness_score", 0),
        "missing_fields": result.get("missing_fields", []),
    }


def classify_risk_node(state: ComplaintAgentState) -> ComplaintAgentState:
    response = reasoning_llm.invoke([
        SystemMessage(content=RISK_CLASSIFICATION_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(state.get("extracted", {}))),
    ])
    result = _safe_json_parse(response.content)
    return {
        "ai_risk_classification": result.get("ai_risk_classification"),
        "ai_risk_rationale": result.get("ai_risk_rationale"),
    }


def summarize_node(state: ComplaintAgentState) -> ComplaintAgentState:
    response = extraction_llm.invoke([
        SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(state.get("extracted", {}))),
    ])
    return {"ai_summary": response.content.strip()}


def build_complaint_graph():
    graph = StateGraph(ComplaintAgentState)

    graph.add_node("extract_fields", extract_fields_node)
    graph.add_node("check_completeness", check_completeness_node)
    graph.add_node("classify_risk", classify_risk_node)
    graph.add_node("summarize", summarize_node)

    graph.add_edge(START, "extract_fields")
    graph.add_edge("extract_fields", "check_completeness")
    graph.add_edge("check_completeness", "classify_risk")
    graph.add_edge("classify_risk", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# Compiled once at import time, reused across requests
complaint_graph = build_complaint_graph()
