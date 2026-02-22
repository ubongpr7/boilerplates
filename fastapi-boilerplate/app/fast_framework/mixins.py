
from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CreateModelMixin(Generic[ModelType, CreateSchemaType]):
    def create(self, *, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class ListModelMixin(Generic[ModelType]):
    def list(self, *, db: Session, request: Request) -> list[ModelType]:
        queryset = self.get_queryset(db)
        queryset = self.filter_queryset(request, queryset)
        paginator = self.get_paginator(request)
        if paginator:
            return paginator.paginate(db, queryset)
        return db.exec(queryset).all()

class RetrieveModelMixin(Generic[ModelType]):
    def retrieve(self, *, db: Session, id: Any) -> ModelType:
        obj = db.get(self.model, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        return obj

class UpdateModelMixin(Generic[ModelType, UpdateSchemaType]):
    def update(self, *, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = db_obj.dict()
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class DestroyModelMixin:
    def destroy(self, *, db: Session, id: Any) -> ModelType:
        obj = db.get(self.model, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        db.delete(obj)
        db.commit()
        return obj
