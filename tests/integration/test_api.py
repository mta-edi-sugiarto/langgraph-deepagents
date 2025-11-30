from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_agent():
    response = client.post("/api/v1/agents", json={"agent_template": "stateful_agent"})
    assert response.status_code == 200
    assert "agent_id" in response.json()


def test_list_agents():
    client.post("/api/v1/agents", json={"agent_template": "stateful_agent"})
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    assert "agents" in response.json()
    assert isinstance(response.json()["agents"], list)


def test_delete_agent():
    create_response = client.post(
        "/api/v1/agents", json={"agent_template": "stateful_agent"}
    )
    agent_id = create_response.json()["agent_id"]
    delete_response = client.delete(f"/api/v1/agents/{agent_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"


def test_chat_with_agent():
    create_response = client.post(
        "/api/v1/agents", json={"agent_template": "stateful_agent"}
    )
    agent_id = create_response.json()["agent_id"]
    chat_response = client.post(
        f"/api/v1/agents/{agent_id}/chat", json={"message": "hello"}
    )
    assert chat_response.status_code == 200
    assert "reply" in chat_response.json()
