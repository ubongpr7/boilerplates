
from fastapi import Request
from sqlmodel import or_, select

class BaseFilterBackend:
    def filter_queryset(self, request: Request, query, view):
        raise NotImplementedError("filter_queryset() must be implemented by a subclass.")

class SearchFilter(BaseFilterBackend):
    search_param = "search"

    def filter_queryset(self, request: Request, query, view):
        search_term = request.query_params.get(self.search_param)
        if not search_term:
            return query

        search_fields = getattr(view, "search_fields", None)
        if not search_fields:
            return query

        search_filters = []
        for field in search_fields:
            search_filters.append(getattr(view.model, field).ilike(f"%{search_term}%"))

        return query.where(or_(*search_filters))

class OrderingFilter(BaseFilterBackend):
    ordering_param = "ordering"

    def filter_queryset(self, request: Request, query, view):
        ordering = request.query_params.get(self.ordering_param)
        if not ordering:
            return query

        ordering_fields = getattr(view, "ordering_fields", None)
        if not ordering_fields:
            return query

        fields = [field.strip() for field in ordering.split(",")]
        valid_fields = []
        for field in fields:
            if field.lstrip("-") in ordering_fields:
                if field.startswith("-"):
                    valid_fields.append(getattr(view.model, field.lstrip("-")).desc())
                else:
                    valid_fields.append(getattr(view.model, field).asc())

        if valid_fields:
            return query.order_by(*valid_fields)

        return query
