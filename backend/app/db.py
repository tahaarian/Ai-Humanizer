import os, uuid, datetime as dt
from sqlalchemy import create_engine, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import get_settings

def now(): return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    picture: Mapped[str] = mapped_column(String(512), default="")
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=now)

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)  # queued|running|done|failed|cancelled
    style: Mapped[str] = mapped_column(String(20), default="academic")
    words: Mapped[int] = mapped_column(Integer, default=0)
    chunks_total: Mapped[int] = mapped_column(Integer, default=0)
    chunks_done: Mapped[int] = mapped_column(Integer, default=0)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)   # wiped when finished
    sample: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # purged after retention
    before: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=now, index=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

_engine = None; _Session = None
def init_db():
    global _engine, _Session
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        d = os.path.dirname(url.replace("sqlite:///", ""))
        if d: os.makedirs(d, exist_ok=True)
    _engine = create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
    _Session = sessionmaker(_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)

def session(): return _Session()
def get_db():
    s = _Session()
    try: yield s
    finally: s.close()
