from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db import models


def init_db(session: Session) -> None:
    role_admin = session.query(models.Role).filter_by(name="ADMIN").one_or_none()
    role_manager = session.query(models.Role).filter_by(name="MANAGER").one_or_none()

    if not role_admin:
        role_admin = models.Role(name="ADMIN")
        session.add(role_admin)
    if not role_manager:
        role_manager = models.Role(name="MANAGER")
        session.add(role_manager)
    session.flush()

    admin_user = session.query(models.User).filter_by(email="admin@local.test").one_or_none()
    if not admin_user:
        admin_user = models.User(
            email="admin@local.test",
            hashed_password=hash_password("Admin123!"),
            full_name="Admin",
            is_active=True,
        )
        session.add(admin_user)
        session.flush()

    if role_admin not in admin_user.roles:
        admin_user.roles.append(role_admin)

    session.commit()
