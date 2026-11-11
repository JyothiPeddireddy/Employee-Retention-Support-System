"""Database engine, connection pooling, and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import get_settings

settings = get_settings()

# Configure engine arguments based on dialect
connect_args = {}
pool_kwargs = {}

if settings.is_sqlite:
    connect_args["check_same_thread"] = False
    if ":memory:" in settings.database_url:
        from sqlalchemy.pool import StaticPool
        pool_kwargs["poolclass"] = StaticPool
else:
    # PostgreSQL connection pooling configuration
    pool_kwargs["pool_size"] = 10
    pool_kwargs["max_overflow"] = 20
    pool_kwargs["pool_pre_ping"] = True

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    **pool_kwargs,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class for SQLAlchemy declarative definitions
Base = declarative_base()


def get_db():
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all registered tables."""
    Base.metadata.create_all(bind=engine)

