from pydantic import BaseModel, Field
from typing import Literal

IntentType = Literal[
    "git_commit",
    "git_create_branch",
    "git_switch_branch",
    "git_delete_branch",
    "git_list_branches",
    "git_current_branch",
    "general_chat"
]

class CommandPayload(BaseModel):
    intent: IntentType = Field(..., description="The intent of the command")
    query: str = Field(..., description="The command to be executed")