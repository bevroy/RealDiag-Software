"""
PostgreSQL Database Module
===========================

Provides database connection, ORM models, and helper functions for data persistence.
Uses SQLAlchemy for ORM and connection pooling.

PATCHED (audit fixes):
- Added mfa_enabled / mfa_pending / mfa_secret / mfa_backup_codes / mfa_enrolled_at
  columns to User so MFA state can actually be persisted (previously the columns
  didn't exist on the ORM model, so mfa_router.py had nothing to write to and its
  persistence lines were commented out).
- to_dict() now exposes mfa_enabled/mfa_enrolled_at (safe to show the user) but
  deliberately excludes mfa_secret and mfa_backup_codes so those never leak into
  a generic API response. Code that needs the raw secret/backup codes should use
  auth_service.get_user_mfa_state(), which reads them directly from the DB row.
- _ensure_user_columns() now also backfills the new mfa_* columns and role on
  pre-existing databases, the same way it already did for password_reset_token.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Try to import SQLAlchemy - graceful fallback if not available
try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, scoped_session, relationship
    from sqlalchemy.pool import QueuePool, NullPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  SQLAlchemy not installed - database features disabled")
    SQLALCHEMY_AVAILABLE = False

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL not set, try to construct from individual components
if not DATABASE_URL:
    db_host = os.getenv("DATABASE_HOST")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME")
    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")

    if all([db_host, db_name, db_user, db_password]):
        # Construct URL without SSL parameters - we'll add them via connect_args
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"📝 Constructed DATABASE_URL from components (host: {db_host})")

if not DATABASE_URL or not SQLALCHEMY_AVAILABLE:
    if not DATABASE_URL:
        logger.warning("⚠️  DATABASE_URL not set - using in-memory storage")
    if not SQLALCHEMY_AVAILABLE:
        logger.warning("⚠️  SQLAlchemy not available - using in-memory storage")
    DATABASE_AVAILABLE = False
    engine = None
    SessionLocal = None
    Base = None
else:
    DATABASE_AVAILABLE = True

    # Use DATABASE_URL and switch to asyncpg driver for better SSL compatibility
    db_url = DATABASE_URL
    connect_args = {}

    if db_url and "postgresql" in db_url:
        import re

        # Strip all SSL parameters and add only what works with Render
        db_url = re.sub(r'[?&]sslmode=[^&]*', '', db_url)
        db_url = re.sub(r'[?&]sslrootcert=[^&]*', '', db_url)
        db_url = re.sub(r'[?&]sslcert=[^&]*', '', db_url)
        db_url = re.sub(r'[?&]sslkey=[^&]*', '', db_url)
        # Clean up trailing separators
        db_url = re.sub(r'\?&', '?', db_url)
        db_url = re.sub(r'[?&]$', '', db_url)

        # Add simple sslmode parameter in the URL
        separator = '&' if '?' in db_url else '?'
        db_url = f"{db_url}{separator}sslmode=require"

        connect_args = {}
        logger.info(f"🔧 Using psycopg2 with sslmode=require in URL")

    # SQLAlchemy engine optimized for Supabase Transaction mode pooler
    # Transaction mode has 6000+ connection limit vs 15 in Session mode
    # With 2 workers: 2 × (5 pool + 10 overflow) = max 30 connections (well under limit)
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        poolclass=QueuePool,
        pool_size=5,              # Connections per worker
        max_overflow=10,          # Additional connections when busy
        pool_pre_ping=True,       # Verify connections are alive
        pool_recycle=3600,        # Recycle connections every hour
        echo=False
    )

    # Session factory
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Base class for ORM models
    Base = declarative_base()

    logger.info("✅ Database engine created successfully")


# Context manager for database sessions
@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Automatically handles commit, rollback, and session cleanup.

    Usage:
        with get_db_session() as db:
            user = db.query(User).filter_by(email=email).first()
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database not available - DATABASE_URL not configured")

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


# ORM Models - only define if database is available
if DATABASE_AVAILABLE and Base is not None:
    # ORM Models
    class User(Base):
        """User account model."""
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String(255), unique=True, nullable=False, index=True)
        email = Column(String(255), unique=True, nullable=False, index=True)
        username = Column(String(255), unique=True, nullable=True, index=True)
        hashed_password = Column(Text, nullable=False)
        full_name = Column(String(255), nullable=True)
        specialty = Column(String(100), nullable=True)
        institution = Column(String(255), nullable=True)
        role = Column(String(50), default="user")
        is_active = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        is_employee = Column(Boolean, default=False)
        email_verified = Column(Boolean, default=False)
        email_verification_token = Column(String(255), nullable=True)
        email_verification_sent_at = Column(DateTime, nullable=True)
        password_reset_token = Column(String(255), nullable=True)
        password_reset_sent_at = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_login = Column(DateTime, nullable=True)
        search_count = Column(Integer, default=0)
        favorite_count = Column(Integer, default=0)

        # --- MFA (added by audit patch) ---
        # mfa_backup_codes is stored as a JSON-encoded string (list of hashed
        # codes) in a Text column, matching the column type already created by
        # backend/migrations/add_mfa_rbac_columns.py. Encode/decode happens in
        # auth_service.get_user_mfa_state()/update_user_mfa_state(), not here,
        # so this model stays a plain 1:1 mirror of the DB schema.
        mfa_enabled = Column(Boolean, default=False)
        mfa_pending = Column(Boolean, default=False)
        mfa_secret = Column(String(255), nullable=True)
        mfa_backup_codes = Column(Text, nullable=True)
        mfa_enrolled_at = Column(DateTime, nullable=True)

        # Relationships
        sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
        search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
        favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
        custom_lists = relationship("CustomList", back_populates="user", cascade="all, delete-orphan")
        settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary.

            Deliberately does NOT include mfa_secret or mfa_backup_codes -
            those are sensitive and callers that need them should go through
            auth_service.get_user_mfa_state() instead of trusting this dict.
            """
            return {
                "user_id": self.user_id,
                "email": self.email,
                "username": self.username,
                "full_name": self.full_name,
                "specialty": self.specialty,
                "institution": self.institution,
                "role": self.role,
                "is_active": self.is_active,
                "is_verified": self.is_verified,
                "is_employee": getattr(self, 'is_employee', False),
                "email_verified": getattr(self, 'email_verified', False),
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "last_login": self.last_login.isoformat() if self.last_login else None,
                "search_count": self.search_count,
                "favorite_count": self.favorite_count,
                "mfa_enabled": bool(getattr(self, "mfa_enabled", False)),
                "mfa_enrolled_at": self.mfa_enrolled_at.isoformat() if getattr(self, "mfa_enrolled_at", None) else None,
            }


    class Session(Base):
        """User session model."""
        __tablename__ = "sessions"

        id = Column(Integer, primary_key=True, index=True)
        session_id = Column(String(255), unique=True, nullable=False, index=True)
        user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
        token = Column(Text, nullable=False)
        expires_at = Column(DateTime, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        # Relationships
        user = relationship("User", back_populates="sessions")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "expires_at": self.expires_at.isoformat(),
                "created_at": self.created_at.isoformat() if self.created_at else None
            }


    class SearchHistory(Base):
        """Search history model."""
        __tablename__ = "search_history"

        id = Column(Integer, primary_key=True, index=True)
        search_id = Column(String(255), unique=True, nullable=False, index=True)
        user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
        symptoms = Column(JSON, nullable=False)  # Store as JSON array
        age = Column(Integer, nullable=True)
        sex = Column(String(20), nullable=True)
        family = Column(String(100), nullable=True)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        result_count = Column(Integer, default=0)
        top_diagnosis = Column(String(255), nullable=True)

        # Relationships
        user = relationship("User", back_populates="search_history")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "search_id": self.search_id,
                "user_id": self.user_id,
                "symptoms": self.symptoms,
                "age": self.age,
                "sex": self.sex,
                "family": self.family,
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "result_count": self.result_count,
                "top_diagnosis": self.top_diagnosis
            }


    class Favorite(Base):
        """Favorite diagnosis model."""
        __tablename__ = "favorites"

        id = Column(Integer, primary_key=True, index=True)
        favorite_id = Column(String(255), unique=True, nullable=False, index=True)
        user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
        rule_id = Column(String(255), nullable=False, index=True)
        diagnosis_label = Column(String(255), nullable=False)
        family = Column(String(100), nullable=True)
        notes = Column(Text, nullable=True)
        added_at = Column(DateTime, default=datetime.utcnow)

        # Relationships
        user = relationship("User", back_populates="favorites")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "favorite_id": self.favorite_id,
                "user_id": self.user_id,
                "rule_id": self.rule_id,
                "diagnosis_label": self.diagnosis_label,
                "family": self.family,
                "notes": self.notes,
                "added_at": self.added_at.isoformat() if self.added_at else None
            }


    class CustomList(Base):
        """Custom differential diagnosis list model."""
        __tablename__ = "custom_lists"

        id = Column(Integer, primary_key=True, index=True)
        list_id = Column(String(255), unique=True, nullable=False, index=True)
        user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
        name = Column(String(255), nullable=False)
        description = Column(Text, nullable=True)
        specialty = Column(String(100), nullable=True)
        diagnoses = Column(JSON, nullable=False)  # Store as JSON array
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_public = Column(Boolean, default=False)

        # Relationships
        user = relationship("User", back_populates="custom_lists")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "list_id": self.list_id,
                "user_id": self.user_id,
                "name": self.name,
                "description": self.description,
                "specialty": self.specialty,
                "diagnoses": self.diagnoses,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "is_public": self.is_public
            }


    class UserSettings(Base):
        """User settings and preferences model."""
        __tablename__ = "user_settings"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String(255), ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
        default_specialty = Column(String(100), nullable=True)
        notification_preferences = Column(JSON, default={})  # Store as JSON object
        display_preferences = Column(JSON, default={})  # Store as JSON object

        # Relationships
        user = relationship("User", back_populates="settings")

        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "user_id": self.user_id,
                "default_specialty": self.default_specialty,
                "notification_preferences": self.notification_preferences or {},
                "display_preferences": self.display_preferences or {}
            }

else:
    # Define placeholder values when database is not available
    User = None
    Session = None
    SearchHistory = None
    Favorite = None
    CustomList = None
    UserSettings = None


# Database initialization
def init_database():
    """
    Initialize database by creating all tables.
    Safe to call multiple times - will not drop existing tables.
    """
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️  Cannot initialize database - DATABASE_URL not configured")
        return False

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        # Apply lightweight column migrations for tables that already exist
        _ensure_user_columns()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def _ensure_user_columns():
    """
    Idempotently add columns to the users table that may be missing on
    pre-existing databases (no formal migration tool is in use).
    Safe to run on every startup.
    """
    if not DATABASE_AVAILABLE:
        return
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            return
        existing = {col["name"] for col in inspector.get_columns("users")}
        wanted = {
            "password_reset_token": "VARCHAR(255)",
            "password_reset_sent_at": "TIMESTAMP",
            # MFA columns - added by audit patch so the ORM model above
            # actually matches what's in the database on upgrade.
            "role": "VARCHAR(50) DEFAULT 'user'",
            "mfa_enabled": "BOOLEAN DEFAULT false",
            "mfa_pending": "BOOLEAN DEFAULT false",
            "mfa_secret": "VARCHAR(255)",
            "mfa_backup_codes": "TEXT",
            "mfa_enrolled_at": "TIMESTAMP",
        }
        with engine.begin() as conn:
            for name, col_type in wanted.items():
                if name not in existing:
                    conn.execute(text(f'ALTER TABLE users ADD COLUMN {name} {col_type}'))
                    logger.info(f"✅ Added column users.{name}")
    except Exception as e:
        logger.warning(f"Column auto-migration skipped: {e}")


def drop_all_tables():
    """
    Drop all tables from database.
    USE WITH CAUTION - This will delete all data!
    """
    if not DATABASE_AVAILABLE:
        logger.warning("⚠️  Cannot drop tables - DATABASE_URL not configured")
        return False

    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ All tables dropped")


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection successful, False otherwise.
    """
    if not DATABASE_AVAILABLE:
        return False

    try:
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Helper functions for common queries
def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by user_id."""
    if not DATABASE_AVAILABLE:
        return None

    with get_db_session() as db:
        return db.query(User).filter_by(user_id=user_id).first()


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    if not DATABASE_AVAILABLE:
        return None

    with get_db_session() as db:
        return db.query(User).filter_by(email=email).first()


def get_user_search_history(user_id: str, limit: int = 50) -> List[SearchHistory]:
    """Get user's search history."""
    if not DATABASE_AVAILABLE:
        return []

    with get_db_session() as db:
        return db.query(SearchHistory)\
            .filter_by(user_id=user_id)\
            .order_by(SearchHistory.timestamp.desc())\
            .limit(limit)\
            .all()


def get_user_favorites(user_id: str) -> List[Favorite]:
    """Get user's favorites."""
    if not DATABASE_AVAILABLE:
        return []

    with get_db_session() as db:
        return db.query(Favorite)\
            .filter_by(user_id=user_id)\
            .order_by(Favorite.added_at.desc())\
            .all()


def get_user_custom_lists(user_id: str) -> List[CustomList]:
    """Get user's custom lists."""
    if not DATABASE_AVAILABLE:
        return []

    with get_db_session() as db:
        return db.query(CustomList)\
            .filter_by(user_id=user_id)\
            .order_by(CustomList.updated_at.desc())\
            .all()


def get_user_settings(user_id: str) -> Optional[UserSettings]:
    """Get user settings."""
    if not DATABASE_AVAILABLE:
        return None

    with get_db_session() as db:
        return db.query(UserSettings).filter_by(user_id=user_id).first()


# Export all models and functions
__all__ = [
    "DATABASE_AVAILABLE",
    "engine",
    "SessionLocal",
    "Base",
    "get_db_session",
    "User",
    "Session",
    "SearchHistory",
    "Favorite",
    "CustomList",
    "UserSettings",
    "init_database",
    "drop_all_tables",
    "check_database_connection",
    "get_user_by_id",
    "get_user_by_email",
    "get_user_search_history",
    "get_user_favorites",
    "get_user_custom_lists",
    "get_user_settings"
]
