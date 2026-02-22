
from fastapi import APIRouter, Request
from sqlmodel import Session, select
from typing import Generic, TypeVar, List
from .pagination import BasePagination
from .filters import BaseFilterBackend

ModelType = TypeVar("ModelType")
SerializerType = TypeVar("SerializerType")

class GenericAPIView(APIRouter, Generic[ModelType, SerializerType]):
    model: ModelType
    serializer_class: SerializerType
    pagination_class: type[BasePagination] = None
    filter_backends: List[type[BaseFilterBackend]] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Session = kwargs.get("db")

    def get_queryset(self, db: Session):
        return select(self.model)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get_paginator(self, request: Request):
        if self.pagination_class:
            return self.pagination_class(request)
        return None

    def filter_queryset(self, request: Request, query):
        for backend in self.filter_backends:
            query = backend().filter_queryset(request, query, self)
        return query
