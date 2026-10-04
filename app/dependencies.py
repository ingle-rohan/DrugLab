"""DrugLab / DrugPedia - FastAPI dependencies and security context.

Provides tenant context resolution, database session injection, and platform admin
verification in full alignment with the Phase 1 multi-tenant architecture.
"""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from .database import ANONYMOUS, TenantContext, get_db
from .models import Tenant, User, UserRole


def resolve_tenant_context(
    request: Request,
    x_tenant_id: Annotated[Optional[str], Header(alias="X-Tenant-ID")] = None,
    x_tenant_slug: Annotated[Optional[str], Header(alias="X-Tenant-Slug")] = None,
    x_platform_admin: Annotated[Optional[str], Header(alias="X-Platform-Admin")] = None,
    tenant_param: Annotated[Optional[str], Query(alias="tenant_id")] = None,
) -> TenantContext:
    """Resolve the tenant context from HTTP headers, query params or token.

    Rules:
    - If already set on request.state by middleware, return that.
    - If x_platform_admin is 'true', mark is_platform_admin = True.
    - If a tenant identifier is supplied (UUID or slug), set tenant_id.
    - If none provided, defaults to ANONYMOUS (tenant_id=None, sees global reference rows only).
    """
    if hasattr(request.state, "tenant_context") and request.state.tenant_context is not None:
        return request.state.tenant_context

    is_admin = (x_platform_admin or "").lower() in ("true", "1", "yes")

    raw_tenant = x_tenant_id or tenant_param
    parsed_tenant_id: Optional[uuid.UUID] = None

    if raw_tenant:
        try:
            parsed_tenant_id = uuid.UUID(raw_tenant)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tenant UUID format: '{raw_tenant}'",
            )

    ctx = TenantContext(
        tenant_id=parsed_tenant_id,
        is_platform_admin=is_admin,
    )
    request.state.tenant_context = ctx
    return ctx


TenantDep = Annotated[TenantContext, Depends(resolve_tenant_context)]
DatabaseDep = Annotated[Session, Depends(get_db)]
