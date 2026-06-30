from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Универсальная обертка для пагинированных ответов"""

    total: Annotated[int, Field(description="Общее количество записей")]
    page: Annotated[int, Field(description="Номер текущей страницы (с 1)")]
    limit: Annotated[int, Field(description="Количество записей на страницу")]
    items: Annotated[list[T], Field(description="Записи текущей страницы")]

    @computed_field
    @property
    def pages(self) -> int:
        """Общее количество страниц"""
        return (self.total + self.limit - 1) // self.limit if self.limit else 0


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: Annotated[int, Field(ge=1, description="Номер страницы")] = 1
    limit: Annotated[
        int, Field(35, ge=1, le=1000, description="Количество записей на страницу")
    ]
