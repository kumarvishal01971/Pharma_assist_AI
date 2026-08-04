from fastapi.testclient import TestClient

import app.agents.graph as graph_module
from app.core import config
from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_endpoint_is_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


def test_cors_settings_support_vercel_origin():
    parsed_origins = config.parse_cors_origins("https://pharma-assist-ai-ten.vercel.app")
    assert parsed_origins == ["https://pharma-assist-ai-ten.vercel.app"]


def test_blank_cors_origin_value_falls_back_to_defaults():
    parsed_origins = config.parse_cors_origins("")
    assert parsed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
        "http://10.0.10.47:5173",
        "http://10.0.2.15:5173",
        "https://pharma-assist-ai-ten.vercel.app",
    ]


def test_blank_cors_origin_regex_falls_back_to_defaults():
    assert config.parse_cors_origin_regex("") == config.DEFAULT_CORS_ALLOWED_ORIGIN_REGEX
    assert config.parse_cors_origin_regex(None) == config.DEFAULT_CORS_ALLOWED_ORIGIN_REGEX


def test_groq_wrapper_falls_back_when_primary_model_is_decommissioned(monkeypatch):
    class DummyBadRequest(Exception):
        pass

    class DummyChatGroq:
        def __init__(self, api_key, model, temperature):
            self.model = model

        def invoke(self, messages):
            if self.model == "gemma2-9b-it":
                raise DummyBadRequest("The model `gemma2-9b-it` has been decommissioned")
            return {"model": self.model, "messages": messages}

    monkeypatch.setattr(graph_module, "ChatGroq", DummyChatGroq)
    monkeypatch.setattr(graph_module, "BadRequestError", DummyBadRequest)

    wrapper = graph_module.CompatibleGroqChat(
        api_key="test-key",
        primary_model="gemma2-9b-it",
        fallback_model="llama-3.1-8b-instant",
        temperature=0,
    )

    result = wrapper.invoke([{"role": "user", "content": "hello"}])
    assert result["model"] == "llama-3.1-8b-instant"
