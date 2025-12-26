import pytest


@pytest.mark.api
@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/ui/client",
        "/ui/client/credit",
        "/ui/manager",
    ],
)
def test_ui_pages_available(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


