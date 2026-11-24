import asyncio, logging, datetime as dt
from sqlalchemy import select, update
from . import rewriter, analyzer
from .config import get_settings
from .db import Job, session, now

log = logging.getLogger("humanizer.jobs")
_queue: asyncio.Queue = asyncio.Queue()
_tasks: list = []

_loop = None

def enqueue(job_id: str):
    if _loop: _loop.call_soon_threadsafe(_queue.put_nowait, job_id)

async def run_job(job_id: str):
    with session() as db:
        job = db.get(Job, job_id)
        if not job or job.status != "queued": return
        job.status = "running"; db.commit()
        text, style, sample = job.input_text or "", job.style, job.sample or ""
    parts = rewriter.chunks(text)
    with session() as db:
        db.execute(update(Job).where(Job.id == job_id).values(chunks_total=len(parts))); db.commit()
    out = []
    try:
        for c in parts:
            with session() as db:
                if db.get(Job, job_id).status == "cancelled": return
            out.append(await rewriter.humanize_chunk(c, style, sample))
            with session() as db:
                db.execute(update(Job).where(Job.id == job_id).values(chunks_done=len(out))); db.commit()
        result = "\n\n".join(out)
        with session() as db:
            j = db.get(Job, job_id)
            if j.status == "cancelled": return
            j.result_text, j.before, j.after = result, analyzer.analyze(text), analyzer.analyze(result)
            j.status, j.input_text, j.sample, j.finished_at = "done", None, None, now()
            db.commit()
    except Exception as e:
        log.exception("job %s failed", job_id)
        msg = "The language model is unavailable." if "connect" in repr(e).lower() else "Processing failed."
        with session() as db:
            j = db.get(Job, job_id)
            j.status, j.error, j.input_text, j.sample, j.finished_at = "failed", msg, None, None, now(); db.commit()

async def _worker():
    while True:
        jid = await _queue.get()
        try: await run_job(jid)
        finally: _queue.task_done()

async def _janitor():
    while True:
        cutoff = now() - dt.timedelta(hours=get_settings().result_retention_hours)
        with session() as db:
            db.execute(update(Job).where(Job.finished_at < cutoff, Job.result_text.is_not(None))
                       .values(result_text=None)); db.commit()
        await asyncio.sleep(600)

def start():
    global _loop, _queue
    _loop = asyncio.get_running_loop(); _queue = asyncio.Queue()
    with session() as db:   # recover interrupted work
        db.execute(update(Job).where(Job.status == "running").values(status="queued", chunks_done=0))
        db.commit()
        ids = db.scalars(select(Job.id).where(Job.status == "queued").order_by(Job.created_at)).all()
    for i in ids: enqueue(i)
    for _ in range(get_settings().worker_concurrency): _tasks.append(asyncio.create_task(_worker()))
    _tasks.append(asyncio.create_task(_janitor()))

def stop():
    for t in _tasks: t.cancel()
    _tasks.clear()
