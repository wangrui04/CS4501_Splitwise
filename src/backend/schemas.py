
from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


Money = Annotated[
    str,
    Field(pattern=r"^(?:\d+(?:\.\d{1,2})?|\.\d{1,2})$"),
]


class Participants(StrictModel):
    mode: Literal["all", "only", "all_except"]
    names: list[str]


class Item(StrictModel):
    name: str
    quantity: int = Field(ge=1)
    unitPrice: Money | None
    participants: Participants


class Charge(StrictModel):
    kind: Literal["tax", "tip", "fee"]
    amount: Money | None
    percent: Money | None
    method: Literal["proportional", "equal"] | None

    @model_validator(mode="after")
    def one_or_other(self):
        if self.amount is not None and self.percent is not None:
            raise ValueError(
                "Charge cannot specify both amount and percent"
            )
        return self


class OpenQuestion(StrictModel):
    field: str
    question: str


class ParsedExpense(StrictModel):
    description: str
    payer: str | None
    items: list[Item]
    charges: list[Charge]
    statedTotal: Money | None
    openQuestions: list[OpenQuestion]


class Share(StrictModel):
    name: str
    cents: int = Field(ge=0)
    summary: str


class ExpensePreview(StrictModel):
    payer: str
    currency: Literal["USD"]
    lineItems: list[dict]
    charges: list[dict]
    totalCents: int = Field(ge=0)
    shares: list[Share]
    validated: bool


class QuestionResponse(StrictModel):
    type: Literal["question"]
    question: str


class PreviewResponse(StrictModel):
    type: Literal["preview"]
    preview: ExpensePreview


class UnresolvedResponse(StrictModel):
    type: Literal["unresolved"]
    reason: str


class ErrorResponse(StrictModel):
    type: Literal["error"]
    message: str


ChatResponse = Union[
    QuestionResponse,
    PreviewResponse,
    UnresolvedResponse,
    ErrorResponse,
]
