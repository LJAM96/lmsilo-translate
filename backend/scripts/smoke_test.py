import os
import pathlib
import sys


def main() -> None:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

    os.environ.setdefault("SKIP_MODEL_LOAD", "true")
    os.environ.setdefault("RATE_LIMIT_ENABLED", "true")
    os.environ.setdefault("RATE_LIMIT_REQUESTS", "2")
    os.environ.setdefault("RATE_LIMIT_WINDOW", "60")

    import app as appmod

    app = appmod.app
    client = app.test_client()

    r = client.get("/health")
    assert r.status_code == 200, r.data

    payload = {"text": "Hola mundo"}
    r1 = client.post("/translate", json=payload)
    r2 = client.post("/translate", json=payload)
    r3 = client.post("/translate", json=payload)
    assert r1.status_code in (200, 400), r1.data
    assert r2.status_code in (200, 400), r2.data
    assert r3.status_code == 429, (r3.status_code, r3.data)

    # Relax rate limiting so subsequent upload tests aren't blocked
    with appmod.rate_limiter._lock:
        appmod.rate_limiter._requests.clear()
        appmod.rate_limiter.max_requests = 100

    r = client.post(
        "/upload",
        data={"file": (appmod.io.BytesIO("Hola\nHello\n".encode("utf-8")), "a.txt")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, (r.status_code, r.data)
    assert r.headers.get("Content-Type", "").startswith("text/plain")

    srt = "1\n00:00:01,000 --> 00:00:02,000\nHola\n\n2\n00:00:03,000 --> 00:00:04,000\nHello\n"
    r = client.post(
        "/upload",
        data={"file": (appmod.io.BytesIO(srt.encode("utf-8")), "a.srt")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, (r.status_code, r.data)

    csv_data = "col1,col2\nHola,mundo\nHello,world\n"
    r = client.post(
        "/upload",
        data={"file": (appmod.io.BytesIO(csv_data.encode("utf-8")), "a.csv")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, (r.status_code, r.data)
    assert r.headers.get("Content-Type", "").startswith("text/csv")

    # Celery not configured in smoke test; these should be unavailable.
    r = client.get("/jobs")
    assert r.status_code == 503, (r.status_code, r.data)

    print("SMOKE_OK")


if __name__ == "__main__":
    main()
