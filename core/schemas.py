from pydantic import BaseModel, Field
from typing import Literal

IntentType = Literal[
    "git_commit",
    "git_create_branch",
    "git_switch_branch",
    "git_delete_branch",
    "git_list_branches",
    "git_current_branch",
    "spotify_play",
    "spotify_pause",
    "spotify_skip",
    "spotify_previous",
    "spotify_info",
    "general_chat"
]

class CommandPayload(BaseModel):
    intent: IntentType = Field(..., description="The intent of the command")
    query: str = Field(..., description="The command to be executed")
    confidence : float = Field(..., ge=0.0, le=1.0, description="Confidence score of the intent classification (0.0 to 1.0)")