import pytest 
from fastapi.testclient import TestClient
import database
from main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def setup_test_db(tmp_path,monkeypatch):
    fake_db=str(tmp_path / "test.db")
    monkeypatch.setattr(database,"db_path",fake_db)
    database.init_db()

def test_create_task():
    res=client.post(
        "/tasks",
        json={"title": "学习pytest", "category": "ai", "estimated_minutes": 30},
    )
    assert res.status_code==201
    assert res.json()["id"]==1

def test_create_wrong_task():
    res=client.post(
        "/tasks",
        json={"title":"吃饭", "category":"dining","estimated_minutes":15},
    )
    assert res.status_code==422

def test_get_tasks():
    client.post(
        "/tasks",
        json={"title": "金钱心理学", "category": "invest", "estimated_minutes": 90},
    )
    client.post(
        "/tasks",
        json={"title": "sql", "category": "ai", "estimated_minutes": 15},
    )

    res_all = client.get("/tasks")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2

    res_ai = client.get("/tasks", params={"category": "ai"})
    assert res_ai.status_code == 200
    assert len(res_ai.json()) == 1
    assert res_ai.json()[0]["title"] == "sql"

def test_finish_task():
    client.post(
        "/tasks",
        json={"title": "卧推训练", "category": "health", "estimated_minutes": 60},
    )
    res_ok = client.patch("/tasks/1/done")
    assert res_ok.status_code == 200
    assert res_ok.json()["is_done"] is True

    res_404 = client.patch("/tasks/999/done")
    assert res_404.status_code == 404


def test_delete_task():
    client.post(
        "/tasks",
        json={"title": "临时任务", "category": "ai", "estimated_minutes": 10},
    )
    res_ok = client.delete("/tasks/1")
    assert res_ok.status_code == 200

    res_404 = client.delete("/tasks/1")
    assert res_404.status_code == 404
