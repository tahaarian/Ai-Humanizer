import logging, datetime as dt
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from starlette.middleware.sessions import SessionMiddleware
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # hide per-poll GET lines
from . import analyzer, files, jobs, llm, db as dbm
from .auth import router as auth_router, current_user, require_admin
from .config import get_settings
from .db import Job, User, get_db, now

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(app):
    dbm.init_db(); jobs.start()
    yield
    jobs.stop()

cfg = get_settings()
app = FastAPI(title="Ai-Humanizer", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=cfg.secret_key, same_site="lax",
                   https_only=cfg.public_url.startswith("https"), max_age=60 * 60 * 24 * 14)
app.include_router(auth_router)

class JobIn(BaseModel):
    text: str = Field(min_length=1)
    style: str = "academic"
    sample: str = ""

class TextIn(BaseModel):
    text: str

def job_dto(j: Job, full=False):
    d = {"id": j.id, "status": j.status, "style": j.style, "words": j.words,
         "progress": (j.chunks_done / j.chunks_total) if j.chunks_total else 0,
         "error": j.error, "created_at": j.created_at.isoformat(),
         "finished_at": j.finished_at.isoformat() if j.finished_at else None,
         "expired": j.status == "done" and j.result_text is None}
    if full: d.update(result=j.result_text, before=j.before, after=j.after)
    return d

def _own(db, user, job_id):
    j = db.get(Job, job_id)
    if not j or j.user_id != user.id: raise HTTPException(404, "Job not found.")
    return j

def _used(db, uid):
    since = now() - dt.timedelta(hours=24)
    return db.scalar(select(func.coalesce(func.sum(Job.words), 0)).where(Job.user_id == uid, Job.created_at > since))

@app.get("/api/health")
async def health(): return {"status": "ok", "llm": await llm.status()}

@app.get("/api/me")
def me(u: User = Depends(current_user), db=Depends(get_db)):
    return {"email": u.email, "name": u.name, "picture": u.picture, "role": u.role,
            "quota": {"used": _used(db, u.id), "limit": cfg.daily_word_limit}}

@app.post("/api/analyze")
def analyze(b: TextIn, u: User = Depends(current_user)): return analyzer.analyze(b.text)

@app.post("/api/extract")
async def extract(file: UploadFile = File(...), u: User = Depends(current_user)):
    data = await file.read()
    if len(data) > 10 * 1024 * 1024: raise HTTPException(413, "File too large (10 MB max).")
    try: return {"text": files.extract(file.filename or "", data)}
    except ValueError as e: raise HTTPException(400, str(e))

@app.post("/api/jobs", status_code=202)
def create_job(b: JobIn, u: User = Depends(current_user), db=Depends(get_db)):
    words = len(b.text.split())
    if words < 30: raise HTTPException(422, "Please provide at least 30 words.")
    if words > cfg.max_words_per_job: raise HTTPException(413, f"Max {cfg.max_words_per_job} words per job.")
    if _used(db, u.id) + words > cfg.daily_word_limit: raise HTTPException(429, "Daily word limit reached.")
    active = db.scalar(select(func.count()).where(Job.user_id == u.id, Job.status.in_(["queued", "running"])))
    if active >= 3: raise HTTPException(429, "Too many active jobs.")
    j = Job(user_id=u.id, style=b.style, words=words, input_text=b.text, sample=b.sample[:2000] or None)
    db.add(j); db.commit(); jobs.enqueue(j.id)
    return job_dto(j)

@app.get("/api/jobs")
def list_jobs(u: User = Depends(current_user), db=Depends(get_db)):
    rows = db.scalars(select(Job).where(Job.user_id == u.id).order_by(Job.created_at.desc()).limit(50)).all()
    return [job_dto(j) for j in rows]

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, u: User = Depends(current_user), db=Depends(get_db)):
    return job_dto(_own(db, u, job_id), full=True)

@app.post("/api/jobs/{job_id}/cancel")
def cancel(job_id: str, u: User = Depends(current_user), db=Depends(get_db)):
    j = _own(db, u, job_id)
    if j.status in ("queued", "running"):
        j.status, j.input_text, j.sample, j.finished_at = "cancelled", None, None, now(); db.commit()
    return job_dto(j)

@app.delete("/api/jobs/{job_id}", status_code=204)
def delete(job_id: str, u: User = Depends(current_user), db=Depends(get_db)):
    j = _own(db, u, job_id); db.delete(j); db.commit()

@app.get("/api/admin/stats")
def stats(a: User = Depends(require_admin), db=Depends(get_db)):
    return {"users": db.scalar(select(func.count(User.id))),
            "jobs": {s: db.scalar(select(func.count()).where(Job.status == s))
                     for s in ("queued", "running", "done", "failed", "cancelled")}}
