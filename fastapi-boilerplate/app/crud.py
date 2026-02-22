import datetime
import uuid
from typing import Any

from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.mainapps.accounts.models import EmailVerificationToken, Item, User
from app.mainapps.accounts.serializers import UserCreate, UserUpdate, ItemCreate






def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def create_superuser(*, session: Session, user_create: UserCreate) -> User:
    user_create.is_superuser = True
    user_create.is_staff = True
    user_create.is_verified = True
    return create_user(session=session, user_create=user_create)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_or_create_sso_user(session: Session, email: str, full_name: str | None) -> User:
    user = get_user_by_email(session=session, email=email)
    if user:
        return user

    password = str(uuid.uuid4())
    user_create = UserCreate(email=email, password=password, full_name=full_name)
    user = create_user(session=session, user_create=user_create)
    return user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item



def create_email_verification_token(
    session: Session,
    user_id: uuid.UUID,
    token: str,
    expires_at: datetime
) -> EmailVerificationToken:
    """Create an email verification token."""
    db_token = EmailVerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token


def get_email_verification_token(
    session: Session,
    user_id: uuid.UUID,
    token: str
) -> EmailVerificationToken | None:
    """Get an email verification token."""
    statement = select(EmailVerificationToken).where(
        (EmailVerificationToken.user_id == user_id) &
        (EmailVerificationToken.token == token) &
        (EmailVerificationToken.is_used == False)
    )
    return session.exec(statement).first()