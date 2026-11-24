import time
TXT = " ".join(["The system measures 12 values and reports results [1] in a clear and simple way."] * 6)

def login(c, email="a@x.com"): c.get("/auth/dev-login", params={"email": email}, follow_redirects=False)

def test_requires_auth(client): assert client.get("/api/me").status_code == 401

def test_job_flow(client):
    login(client)
    r = client.post("/api/jobs", json={"text": TXT}); assert r.status_code == 202
    jid = r.json()["id"]
    for _ in range(50):
        j = client.get(f"/api/jobs/{jid}").json()
        if j["status"] in ("done", "failed"): break
        time.sleep(0.1)
    assert j["status"] == "done" and "[1]" in j["result"] and j["progress"] == 1
    assert len(client.get("/api/jobs").json()) == 1

def test_isolation(client):
    login(client, "a@x.com")
    jid = client.post("/api/jobs", json={"text": TXT}).json()["id"]
    client.post("/auth/logout"); login(client, "b@x.com")
    assert client.get(f"/api/jobs/{jid}").status_code == 404

def test_short_text_and_admin(client):
    login(client, "b@x.com")
    assert client.post("/api/jobs", json={"text": "too short"}).status_code == 422
    assert client.get("/api/admin/stats").status_code == 403
    client.post("/auth/logout"); login(client, "admin@x.com")
    assert client.get("/api/admin/stats").status_code == 200
