from app.database import platform_admin_session, tenant_session
from app.models import Drug, Tenant

with platform_admin_session() as s:
    a, b = Tenant(name="A", slug="tenant-a"), Tenant(name="B", slug="tenant-b")
    s.add_all([a, b])
    s.flush()
    s.add_all([
        Drug(generic_name="Ibuprofen"),                    # global row
        Drug(generic_name="A-private", tenant_id=a.id),    # private to tenant A
    ])
    ids = (a.id, b.id)

for name, tid in zip("AB", ids):
    with tenant_session(tid) as s:
        print(name, sorted(d.generic_name for d in s.query(Drug)))