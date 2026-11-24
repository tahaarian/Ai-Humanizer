import os, tempfile, pytest
os.environ.update(DEV_LOGIN="true", DATABASE_URL=f"sqlite:///{tempfile.mkdtemp()}/t.db", PUBLIC_URL="http://testserver", ADMIN_EMAILS="admin@x.com")
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch):
    async def fake(system, user, temperature=0.9):
        return user
    monkeypatch.setattr("app.llm.chat", fake)
    from app.main import app
    with TestClient(app) as c:
        yield c
