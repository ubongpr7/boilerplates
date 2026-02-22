
from typing import Generic, Optional, TypeVar
from fastapi import Request
from pydantic import BaseModel
from sqlmodel import Session, select, func

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    page: int
    size: int
    total: int
    items: list[T]
    next_page: Optional[int] = None
    previous_page: Optional[int] = None


class BasePagination:
    def __init__(self, request: Request, page: int = 1, size: int = 10):
        self.request = request
        self.page = page
        self.size = size

    def paginate(self, db: Session, query, **kwargs):
        raise NotImplementedError("paginate() must be implemented by a subclass.")


class PageNumberPagination(BasePagination):
    def paginate(self, db: Session, query, **kwargs):
        total = db.exec(select(func.count()).select_from(query.subquery())).one()
        items = db.exec(query.offset((self.page - 1) * self.size).limit(self.size)).all()

        next_page = self.page + 1 if self.page * self.size < total else None
        previous_page = self.page - 1 if self.page > 1 else None

        return Page(
            page=self.page,
            size=self.size,
            total=total,
            items=items,
            next_page=next_page,
            previous_page=previous_page,
        )
