import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import create_access_token
from app.db import Base
from app.deps import get_db
from app.main import app
from app.models import Permission, Role, User
from app.seed import seed_data


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_data(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_login_success(client):
    response = client.post("/auth/login", json={"email": "admin@local.test", "password": "Admin123!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_denied_for_non_admin(client, db_session):
    role = db_session.query(Role).filter(Role.name == "GUARD").first()
    user = User(email="guard@local.test", hashed_password="hashed", is_active=True)
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()

    access = create_access_token(user.email)

    response = client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {access}"},
        json={"email": "new@local.test", "password": "Password123!"},
    )
    assert response.status_code == 403
