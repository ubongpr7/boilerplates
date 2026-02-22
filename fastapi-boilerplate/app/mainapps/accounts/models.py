import uuid
from datetime import date, datetime, timedelta

from pydantic import EmailStr, validator, model_validator
from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

SEX_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Prefer not to say", "Prefer not to say")]
PREFER_NOT_TO_SAY = "Prefer not to say"

def validate_adult(value):
    if value and value > date.today() - timedelta(days=18 * 365):
        raise ValueError("You must be above 18 years of age.")
    return value



# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    username: str | None = Field(default=None, max_length=150, unique=True)
    first_name: str | None = Field(default=None, max_length=150)
    last_name: str | None = Field(default=None, max_length=150)
    sex: str | None = Field(default=PREFER_NOT_TO_SAY, max_length=20)
    date_of_birth: date | None = Field(default=None)
    phone_number: str | None = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    role: str | None = Field(default=None, max_length=20)
    last_login_ip: str | None = Field(default=None)
    last_login: datetime | None = Field(default=None)

    _validate_dob = validator("date_of_birth", allow_reuse=True)(validate_adult)



# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "accounts_user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    verification_tokens: list["EmailVerificationToken"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    class Config:
        table_args = (
            Index("ix_accounts_user_email", "email"),
            Index("ix_accounts_user_is_verified", "is_verified"),
        )

    @property
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="accounts_user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")

class EmailVerificationToken(SQLModel, table=True):
    __tablename__ = "email_verification_tokens"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="accounts_user.id", nullable=False, ondelete="CASCADE")
    token: str = Field(unique=True, index=True)  # Random token
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(nullable=False)  # 24 hours from creation
    is_used: bool = Field(default=False)
    
    user: User | None = Relationship(back_populates="verification_tokens")