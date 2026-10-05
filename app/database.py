"""DrugLab / DrugPedia - engine, sessions, tenant context and row-level security.

Tenancy model
-------------
* Tenant-scoped tables carry ``tenant_id``. NULL = global reference data
  (readable by all tenants, writable only by platform admins); a value = private
  to that tenant.
* Every transaction starts with ``set_config('app.current_tenant', ...)`` and
  ``set_config('app.is_platform_admin', ...)`` (see the ``after_begin`` hook), and
  PostgreSQL row-level security enforces the rules even if an API route forgets
  a ``WHERE tenant_id = ...`` clause.
* The application must connect as a NON-superuser role that does not own the
  tables (superusers and table owners bypass RLS). ``FORCE ROW LEVEL SECURITY``
  also covers the owner role.
* Authentication code that must look a user up before the tenant is known should
  use ``platform_admin_session()`` and nothing else should.
"""

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker

from .models import Base, TenantScopedMixin


import os

DEFAULT_NEON_DB_URL = (
    "postgresql+psycopg://druglab_app:DrugLabApp2026x"
    "@ep-jolly-bonus-b3ccfxu6.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)


def normalize_database_url(url: Optional[str]) -> str:
    """Ensure database URL is non-empty and uses postgresql+psycopg dialect."""
    if not url or not url.strip():
        return DEFAULT_NEON_DB_URL
    raw = url.strip()
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw[len("postgres://"):]
    if raw.startswith("postgresql://") and not raw.startswith("postgresql+"):
        return "postgresql+psycopg://" + raw[len("postgresql://"):]
    return raw


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DRUGLAB_", env_file=".env", extra="ignore")

    database_url: str = DEFAULT_NEON_DB_URL
    sql_echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle_seconds: int = 1800
    hnsw_ef_search: int = 64  # pgvector recall / latency trade-off per session


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    # Check OS environment for DRUGLAB_DATABASE_URL or DATABASE_URL
    env_url = os.getenv("DRUGLAB_DATABASE_URL") or os.getenv("DATABASE_URL")
    if env_url:
        settings.database_url = normalize_database_url(env_url)
    else:
        settings.database_url = normalize_database_url(settings.database_url)
    return settings


# --------------------------------------------------------------------------
# Engine & session factory
# --------------------------------------------------------------------------
def build_engine(settings: Optional[Settings] = None) -> Engine:
    s = settings or get_settings()
    db_url = normalize_database_url(s.database_url)
    return create_engine(
        db_url,
        echo=s.sql_echo,
        pool_size=s.pool_size,
        max_overflow=s.max_overflow,
        pool_recycle=s.pool_recycle_seconds,
        pool_pre_ping=True,
        future=True,
    )


engine: Engine = build_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=Session
)


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Set by the authentication layer on ``request.state.tenant_context``."""

    tenant_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID] = None
    is_platform_admin: bool = False


ANONYMOUS = TenantContext(tenant_id=None)  # sees global reference rows only


@event.listens_for(SessionLocal, "after_begin")
def _apply_tenant_context(session: Session, transaction: SessionTransaction, connection: Connection) -> None:
    """Re-apply the tenant context at the start of EVERY transaction (is_local=true)."""
    ctx: TenantContext = session.info.get("tenant_context", ANONYMOUS)
    connection.execute(
        text(
            "SELECT set_config('app.current_tenant', :tenant, true), "
            "set_config('app.is_platform_admin', :admin, true), "
            "set_config('hnsw.ef_search', :ef, true)"
        ),
        {
            "tenant": str(ctx.tenant_id) if ctx.tenant_id else "",
            "admin": "true" if ctx.is_platform_admin else "false",
            "ef": str(get_settings().hnsw_ef_search),
        },
    )


def _new_session(ctx: TenantContext) -> Session:
    return SessionLocal(info={"tenant_context": ctx})


# --------------------------------------------------------------------------
# FastAPI dependency & context managers
# --------------------------------------------------------------------------
def get_db(request: Request) -> Iterator[Session]:
    """Request-scoped session bound to the caller's tenant.

    Commits when the route returns normally, rolls back on any exception.
    Without an authenticated ``request.state.tenant_context`` the session can
    only see global rows (secure by default).
    """
    ctx: TenantContext = getattr(request.state, "tenant_context", ANONYMOUS)
    session = _new_session(ctx)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def tenant_session(tenant_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> Iterator[Session]:
    """For background jobs (embedding refresh, imports) acting for one tenant."""
    session = _new_session(TenantContext(tenant_id=tenant_id, user_id=user_id))
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def platform_admin_session() -> Iterator[Session]:
    """Bypasses tenant filtering. Use ONLY for login lookups, seeding global reference
    data and platform maintenance."""
    session = _new_session(TenantContext(tenant_id=None, is_platform_admin=True))
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --------------------------------------------------------------------------
# Initialisation: extensions, tables, row-level security
# --------------------------------------------------------------------------
RLS_HELPER_FUNCTIONS = (
    """
    CREATE OR REPLACE FUNCTION app_current_tenant() RETURNS uuid
    LANGUAGE sql STABLE AS
    $$ SELECT NULLIF(current_setting('app.current_tenant', true), '')::uuid $$
    """,
    """
    CREATE OR REPLACE FUNCTION app_is_platform_admin() RETURNS boolean
    LANGUAGE sql STABLE AS
    $$ SELECT COALESCE(current_setting('app.is_platform_admin', true), 'false') = 'true' $$
    """,
)


def tenant_scoped_tables() -> list[str]:
    """Tables with a nullable tenant_id (global + private rows)."""
    return sorted(
        m.class_.__tablename__
        for m in Base.registry.mappers
        if issubclass(m.class_, TenantScopedMixin)
    )


def _enable_rls(conn: Connection, table: str, *, allow_global_read: bool) -> None:
    conn.execute(text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
    conn.execute(text(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY'))
    for policy in ("tenant_read", "tenant_write"):
        conn.execute(text(f'DROP POLICY IF EXISTS {policy} ON "{table}"'))
    if allow_global_read:
        conn.execute(
            text(
                f'CREATE POLICY tenant_read ON "{table}" FOR SELECT USING '
                "(tenant_id IS NULL OR tenant_id = app_current_tenant() OR app_is_platform_admin())"
            )
        )
    conn.execute(
        text(
            f'CREATE POLICY tenant_write ON "{table}" FOR ALL '
            "USING (tenant_id = app_current_tenant() OR app_is_platform_admin()) "
            "WITH CHECK (tenant_id = app_current_tenant() OR app_is_platform_admin())"
        )
    )


def apply_row_level_security(conn: Connection) -> None:
    for stmt in RLS_HELPER_FUNCTIONS:
        conn.execute(text(stmt))
    for table in tenant_scoped_tables():
        _enable_rls(conn, table, allow_global_read=True)
    # users: strictly private to the tenant (no global rows)
    _enable_rls(conn, "users", allow_global_read=False)
    # tenants: a tenant sees only itself
    conn.execute(text('ALTER TABLE "tenants" ENABLE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE "tenants" FORCE ROW LEVEL SECURITY'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_self ON "tenants"'))
    conn.execute(
        text(
            'CREATE POLICY tenant_self ON "tenants" FOR ALL '
            "USING (id = app_current_tenant() OR app_is_platform_admin()) "
            "WITH CHECK (app_is_platform_admin())"
        )
    )


def init_db(eng: Optional[Engine] = None) -> None:
    """Create extensions, tables and RLS policies. Safe to run repeatedly.

    This is for local bootstrap and tests; production schema changes go through
    Alembic (set ``target_metadata = app.models.Base.metadata`` in env.py and
    call ``apply_row_level_security`` from a migration).
    The connecting role needs CREATE on the database (and permission to create
    the ``vector`` and ``pg_trgm`` extensions) when this runs.
    """
    target = eng or engine
    with target.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        Base.metadata.create_all(conn)
        apply_row_level_security(conn)


def check_db_health(session: Session) -> dict[str, str]:
    """Used by /health: verifies connectivity, pgvector and the tenant context."""
    version = session.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")).scalar()
    tenant = session.execute(text("SELECT app_current_tenant()")).scalar()
    return {
        "database": "ok",
        "pgvector": version or "missing",
        "tenant_context": str(tenant) if tenant else "none",
    }
