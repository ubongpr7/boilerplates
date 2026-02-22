import uuid
from datetime import date, datetime, timedelta

from pydantic import EmailStr, validator, model_validator
from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel
