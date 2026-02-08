from sqlalchemy.orm import Session

from app import models
from app.auth import hash_password

DEFAULT_PERMISSIONS = [
    "USER:MANAGE",
    "BUILDING:READ",
    "BUILDING:WRITE",
]

DEFAULT_ROLES = [
    "ADMIN",
    "MANAGER",
    "ACCOUNTANT",
    "GUARD",
]


def seed_data(db: Session) -> None:
    existing_users = db.query(models.User).count()
    if existing_users > 0:
        return

    permissions = []
    for code in DEFAULT_PERMISSIONS:
        permission = models.Permission(code=code)
        db.add(permission)
        permissions.append(permission)

    roles = []
    for name in DEFAULT_ROLES:
        role = models.Role(name=name)
        db.add(role)
        roles.append(role)

    db.flush()

    admin_role = next(role for role in roles if role.name == "ADMIN")
    admin_role.permissions = permissions

    admin = models.User(
        email="admin@local.test",
        hashed_password=hash_password("Admin123!"),
        full_name="Admin",
        is_active=True,
    )
    admin.roles.append(admin_role)
    db.add(admin)
    db.commit()
