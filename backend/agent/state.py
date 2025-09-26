from typing import Annotated
from langgraph.graph.message import Messages

from pydantic import BaseModel, Field
from langgraph.graph import add_messages


class LegalAgentState(BaseModel):
    messages: Annotated[list[Messages], add_messages]
    question: str = Field(..., description="The question to be answered.")
    legal_field: str | None = Field(
        default=None, description="The legal field of the user's question"
    )
    case_category: str | None = Field(
        default=None,
        description="The determined case category of the user's question/case.",
    )
