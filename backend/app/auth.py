from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from .config import get_settings
from .db import User, get_db

router = APIRouter()
oauth = OAuth()
_s = get_settings()
if _s.google_client_id:
    oauth.register("google", client_id=_s.google_client_id, client_secret=_s.google_client_secret,
                   server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                   client_kwargs={"scope": "openid email profile"})

def _upsert(db, email, name="", picture=""):
    s = get_settings(); email = email.lower()
    if s.domains and email.split("@")[-1] not in s.domains:
        raise HTTPException(403, "This email domain is not allowed.")
    u = db.scalar(select(User).where(User.email == email))
    if not u:
        u = User(email=email, role="admin" if email in s.admins else "user"); db.add(u)
    u.name, u.picture = name or u.name, picture or u.picture
    if email in s.admins: u.role = "admin"
    db.commit(); return u

@router.get("/auth/login")
async def login(request: Request):
    if "google" not in oauth._clients: raise HTTPException(503, "Google login is not configured.")
    return await oauth.google.authorize_redirect(request, f"{get_settings().public_url}/auth/callback")

@router.get("/auth/callback")
async def callback(request: Request, db=Depends(get_db)):
    try: token = await oauth.google.authorize_access_token(request)
    except Exception: raise HTTPException(400, "Google sign-in failed.")
    info = token.get("userinfo") or {}
    if not info.get("email") or not info.get("email_verified", False):
        raise HTTPException(403, "Verified Google email required.")
    u = _upsert(db, info["email"], info.get("name", ""), info.get("picture", ""))
    request.session["uid"] = u.id
    return RedirectResponse(get_settings().public_url + "/app")

@router.get("/auth/dev-login")
def dev_login(request: Request, email: str = "dev@example.com", db=Depends(get_db)):
    if not get_settings().dev_login: raise HTTPException(404)
    request.session["uid"] = _upsert(db, email, "Dev User").id
    return RedirectResponse(get_settings().public_url + "/app")

@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear(); return {"ok": True}

def current_user(request: Request, db=Depends(get_db)) -> User:
    uid = request.session.get("uid")
    u = db.get(User, uid) if uid else None
    if not u: raise HTTPException(401, "Not signed in.")
    return u

def require_admin(u: User = Depends(current_user)) -> User:
    if u.role != "admin": raise HTTPException(403, "Admin only.")
    return u
