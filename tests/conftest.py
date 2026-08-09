from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.dependencies.database import get_db
from app.main import app
from app.models import Base
from app.models.enums import UserRole
from app.models.user import User

# In-memory SQLite shared across connections for the whole test session.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _db_schema():
    """Fresh schema per test for isolation."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_infra(monkeypatch):
    """Keep tests hermetic: mock the RabbitMQ publisher and Redis cache."""
    published = MagicMock()
    monkeypatch.setattr("app.services.case_service.publish_event", published)

    store: dict = {}
    monkeypatch.setattr(
        "app.services.case_service.cache_get", lambda k: store.get(k)
    )
    monkeypatch.setattr(
        "app.services.case_service.cache_set",
        lambda k, v, ttl_seconds=60: store.__setitem__(k, v),
    )
    monkeypatch.setattr(
        "app.services.case_service.cache_delete",
        lambda *keys: [store.pop(k, None) for k in keys],
    )
    return {"published": published, "cache": store}


def _make_user(db, role: UserRole, email: str) -> User:
    user = User(
        full_name=f"{role.value} user",
        email=email,
        password=hash_password("Password123!"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def user_factory(db):
    created: dict[UserRole, User] = {}

    def _factory(role: UserRole) -> User:
        if role not in created:
            created[role] = _make_user(db, role, f"{role.value}@who.int")
        return created[role]

    return _factory


@pytest.fixture()
def auth_headers(user_factory):
    def _headers(role: UserRole) -> dict:
        user = user_factory(role)
        token = create_access_token(
            {"sub": user.email, "role": user.role.value, "uid": user.id}
        )
        return {"Authorization": f"Bearer {token}"}

    return _headers
