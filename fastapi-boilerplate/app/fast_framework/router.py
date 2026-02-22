
from fastapi import APIRouter
from .viewsets import ModelViewSet
from typing import Any

class SimpleRouter(APIRouter):
    def register(
        self,
        prefix: str,
        viewset: type[ModelViewSet],
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Registers a viewset with the router.

        Args:
            prefix (str): The URL prefix for the viewset.
            viewset (type[ModelViewSet]): The viewset class.
        """
        
        # We need to instantiate the viewset to access its methods
        vs_instance = viewset()

        if hasattr(vs_instance, "list"):
            self.add_api_route(
                f"/{prefix}",
                vs_instance.list,
                methods=["GET"],
                response_model=list[vs_instance.serializer_class],
                summary=f"List {vs_instance.model.__name__}s",
            )

        if hasattr(vs_instance, "create"):
            self.add_api_route(
                f"/{prefix}",
                vs_instance.create,
                methods=["POST"],
                response_model=vs_instance.serializer_class,
                summary=f"Create a new {vs_instance.model.__name__}",
                status_code=201,
            )

        if hasattr(vs_instance, "retrieve"):
            self.add_api_route(
                f"/{prefix}/{{id}}",
                vs_instance.retrieve,
                methods=["GET"],
                response_model=vs_instance.serializer_class,
                summary=f"Retrieve a {vs_instance.model.__name__}",
            )

        if hasattr(vs_instance, "update"):
            self.add_api_route(
                f"/{prefix}/{{id}}",
                vs_instance.update,
                methods=["PUT", "PATCH"],
                response_model=vs_instance.serializer_class,
                summary=f"Update a {vs_instance.model.__name__}",
            )

        if hasattr(vs_instance, "destroy"):
            self.add_api_route(
                f"/{prefix}/{{id}}",
                vs_instance.destroy,
                methods=["DELETE"],
                summary=f"Delete a {vs_instance.model.__name__}",
                status_code=204,
            )
