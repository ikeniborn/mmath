import argparse
import asyncio
import getpass
import os
from datetime import datetime, timezone

from sqlalchemy import select, update

from mental_math.accounts.models import Account, AuthSession
from mental_math.accounts.security import hasher, now
from mental_math.db import session_factory


async def reset_password(database_url: str, email: str, password: str) -> None:
    if not 12 <= len(password) <= 128:
        raise ValueError("Password must contain 12–128 characters")
    factory = session_factory(database_url)
    async with factory() as db:
        async with db.begin():
            account = await db.scalar(select(Account).where(Account.email == email.lower()).with_for_update())
            if account is None:
                raise ValueError("Account not found")
            account.password_hash = hasher.hash(password)
            await db.execute(update(AuthSession).where(AuthSession.account_id == account.id, AuthSession.revoked_at.is_(None)).values(revoked_at=now()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Operator-assisted account recovery")
    parser.add_argument("email", help="Exact account email to reset")
    args = parser.parse_args()
    database_url = os.environ.get("MMATH_DATABASE_URL")
    if not database_url:
        parser.error("MMATH_DATABASE_URL is required")
    email = args.email.lower()
    if input(f"Type {email} to confirm account recovery: ").strip().lower() != email:
        parser.error("Account confirmation did not match")
    password = getpass.getpass("New password: ")
    if getpass.getpass("Repeat new password: ") != password:
        parser.error("Passwords did not match")
    asyncio.run(reset_password(database_url, email, password))
    print(f"Password reset and sessions revoked for {email}")


if __name__ == "__main__":
    main()
