from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

router = APIRouter(tags=["ui"])

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def _file(name: str) -> FileResponse:
    p = STATIC_DIR / name
    if not p.exists():
        raise HTTPException(status_code=404, detail="UI file not found")
    return FileResponse(p)


@router.get("/")
async def index() -> FileResponse:
    return _file("index.html")


@router.get("/ui")
async def ui_root(req: Request):
    role = req.session.get("role")
    if role == "client":
        return RedirectResponse("/ui/client", status_code=302)
    if role == "manager":
        return RedirectResponse("/ui/manager", status_code=302)
    return RedirectResponse("/", status_code=302)


@router.get("/ui/client")
async def ui_client() -> FileResponse:
    return _file("client.html")


@router.get("/ui/manager")
async def ui_manager() -> FileResponse:
    return _file("manager.html")


