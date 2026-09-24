"""Promote an existing account to administrator from a trusted shell."""

import argparse

from sqlalchemy import select

from app.database.models import AuditLog, User, UserRole
from app.database.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="email of an existing account to promote")
    args = parser.parse_args()
    email = args.email.strip().lower()
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if user is None:
            parser.error("account not found; register it before promotion")
        if user.role == UserRole.ADMIN:
            print(f"{email} is already an administrator")
            return
        confirmation = input(f"Promote {email} to ADMIN? Type the email to confirm: ")
        if confirmation.strip().lower() != email:
            parser.error("confirmation did not match; no changes made")
        previous = user.role.value
        user.role = UserRole.ADMIN
        session.add(AuditLog(actor_id=user.id, action="user.admin_bootstrap", entity_type="user", entity_id=user.id, details={"from": previous, "to": "ADMIN"}))
        session.commit()
        print(f"Promoted {email} to ADMIN. Sign in again to receive an administrator token.")


if __name__ == "__main__":
    main()
