from at_mind.app.api import healthz

def test_health():
    assert healthz()["ok"] is True
