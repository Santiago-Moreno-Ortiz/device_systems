import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setenv("API_KEY", "test-secret")

    def test_db():
        with sessions() as db:
            yield db

    main.app.dependency_overrides[get_db] = test_db
    try:
        with TestClient(main.app, raise_server_exceptions=False) as api:
            yield api
    finally:
        main.app.dependency_overrides.clear()
        engine.dispose()


def create(client, **changes):
    payload = {"name": "Ana Perez", "email": "ana@example.com"}
    payload.update(changes)
    response = client.post("/users", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_and_filters(client):
    assert client.get("/users").json() == {"total": 0, "items": []}
    user = create(client, name="  Ana Perez  ", email="ANA@example.com")
    uid = user["id"]
    assert user == {"id": uid, "name": "Ana Perez", "email": "ana@example.com", "role": "user", "is_active": True}
    assert client.get(f"/users/{uid}").json() == user
    assert client.get("/users?role=admin").json()["total"] == 0
    response = client.put(f"/users/{uid}", json={"name": "Ana Maria", "email": "ana@example.com", "role": "admin", "is_active": False})
    assert response.status_code == 200
    assert client.get("/users?role=admin&is_active=false").json()["total"] == 1
    response = client.patch(f"/users/{uid}", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    assert response.json()["is_active"] is True
    assert client.get("/users?is_active=false").json()["total"] == 0
    assert client.delete(f"/users/{uid}").status_code == 401
    assert client.delete(f"/users/{uid}", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.delete(f"/users/{uid}", headers={"X-API-Key": "test-secret"}).status_code == 200
    assert client.get(f"/users/{uid}").status_code == 404


@pytest.mark.parametrize("name", ["   ", " a ", "ab", "x" * 81])
@pytest.mark.parametrize("method", ["post", "put", "patch"])
def test_invalid_names(client, name, method):
    uid = create(client)["id"]
    payload = {"name": name, "email": "new@example.com", "role": "user", "is_active": True}
    path = "/users" if method == "post" else f"/users/{uid}"
    assert getattr(client, method)(path, json=payload).status_code == 422


@pytest.mark.parametrize("field", ["name", "email", "role", "is_active"])
def test_patch_rejects_null(client, field):
    user = create(client)
    assert client.patch(f"/users/{user['id']}", json={field: None}).status_code == 422
    assert client.get(f"/users/{user['id']}").json() == user


def test_invalid_payloads(client):
    uid = create(client)["id"]
    assert client.patch(f"/users/{uid}", json={}).status_code == 400
    assert client.put(f"/users/{uid}", json={"name": "Ana Maria"}).status_code == 422
    for changes in ({"email": "invalid"}, {"role": "owner"}, {"is_active": "invalid"}):
        assert client.post("/users", json={"name": "Ana Perez", "email": "new@example.com", **changes}).status_code == 422
    assert client.get("/users?role=owner").status_code == 422
    assert client.get("/users?is_active=invalid").status_code == 422


def test_duplicate_email_and_rollback(client):
    first = create(client)
    second = create(client, email="second@example.com")
    assert client.post("/users", json={"name": "Other User", "email": "ANA@example.com"}).status_code == 400
    for method in ("put", "patch"):
        response = getattr(client, method)(f"/users/{second['id']}", json={"name": "Other User", "email": "ANA@example.com", "role": "user", "is_active": True})
        assert response.status_code == 400
        assert client.get(f"/users/{second['id']}").json() == second
    assert client.get(f"/users/{first['id']}").json() == first


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_missing_user(client, method):
    kwargs = {"headers": {"X-API-Key": "test-secret"}}
    if method in ("put", "patch"):
        kwargs["json"] = {"name": "Ana Perez", "email": "ana@example.com", "role": "user", "is_active": True}
    assert getattr(client, method)("/users/999", **kwargs).status_code == 404


def test_metadata_and_docs(client):
    root = client.get("/")
    assert root.status_code == 200
    assert root.headers["X-API-Version"] == root.json()["version"]
    assert root.headers["X-App-Name"] == "device_systems"
    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == root.json()["version"]
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200


def test_empty_configured_key_is_not_authorized(client, monkeypatch):
    uid = create(client)["id"]
    monkeypatch.setenv("API_KEY", "")
    assert client.delete(f"/users/{uid}", headers={"X-API-Key": ""}).status_code == 401


def test_database_error_hides_details(client, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    def broken_query(*args, **kwargs):
        raise SQLAlchemyError("private database information")

    monkeypatch.setattr(main.user_routes.user_service, "list_users", broken_query)
    response = client.get("/users")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno de base de datos"}
