
from .generics import GenericAPIView
from .mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")
SerializerType = TypeVar("SerializerType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class ViewSet(GenericAPIView):
    pass

class GenericViewSet(
    ViewSet,
    Generic[ModelType, SerializerType, CreateSchemaType, UpdateSchemaType]
):
    pass

class ModelViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    Generic[ModelType, SerializerType, CreateSchemaType, UpdateSchemaType]
):
    pass
