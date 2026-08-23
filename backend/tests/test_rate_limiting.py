"""Rate limiting: the mechanism itself in isolation, plus confirmation that
it's actually wired onto the real login route (the highest-risk unauthenticated
endpoint - credential stuffing)."""
import time

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.rate_limit import rate_limit


def test_rate_limit_blocks_after_max_then_recovers_after_window():
    probe_app = FastAPI()

    @probe_app.get("/limited", dependencies=[Depends(rate_limit("unit-test-recover", max_requests=3, window_seconds=1))])
    def limited():
        return {"ok": True}

    probe_client = TestClient(probe_app)

    for _ in range(3):
        assert probe_client.get("/limited").status_code == 200
    assert probe_client.get("/limited").status_code == 429

    time.sleep(1.1)
    assert probe_client.get("/limited").status_code == 200


def test_rate_limit_buckets_are_independent_per_key():
    probe_app = FastAPI()

    @probe_app.get("/a", dependencies=[Depends(rate_limit("unit-test-bucket-a", max_requests=1, window_seconds=60))])
    def route_a():
        return {"ok": True}

    @probe_app.get("/b", dependencies=[Depends(rate_limit("unit-test-bucket-b", max_requests=1, window_seconds=60))])
    def route_b():
        return {"ok": True}

    probe_client = TestClient(probe_app)

    assert probe_client.get("/a").status_code == 200
    assert probe_client.get("/a").status_code == 429
    assert probe_client.get("/b").status_code == 200  # independent budget, not exhausted by /a


def test_login_route_is_rate_limited(client):
    # 10 requests/60s is the configured limit on /api/auth/login. Wrong
    # credentials return 401 quickly with no real Supabase network cost.
    responses = [
        client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
        for _ in range(11)
    ]
    statuses = [r.status_code for r in responses]

    assert statuses[:10] == [401] * 10
    assert statuses[10] == 429
