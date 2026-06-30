from typing import Annotated

from pydantic import BaseModel, Field


class FilterOption(BaseModel):
    """Универсальная схема для элемента фильтра-селекта"""

    value: Annotated[
        str, Field(description="Значение опции (ID или строковое значение)")
    ]
    label: Annotated[str, Field(description="Отображаемый текст опции")]
