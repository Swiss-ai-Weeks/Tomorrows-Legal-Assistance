from typing import Annotated, Literal
from langgraph.graph.message import Messages

from pydantic import BaseModel, Field
from langgraph.graph import add_messages


class LegalAgentState(BaseModel):
    messages: Annotated[list[Messages], add_messages]
    question: str = Field(..., description="The question to be answered.")
    legal_field: Literal["Arbeitsrecht", "Verkehrsrecht", "andere"] | None = None
