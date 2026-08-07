# Imports
from pydantic import BaseModel, Field
from typing import Literal

# IntentType defines the possible intents for commands that can be executed
IntentType = Literal[
    # Git commands
    "git_commit",
    "git_create_branch",
    "git_current_branch",
    "git_delete_branch",
    "git_list_branches",
    "git_switch_branch",

    # Spotify commands
    "spotify_info",
    "spotify_pause",
    "spotify_play",
    "spotify_previous",
    "spotify_skip",

    # General commands
    "general_chat"
]

# Structure of the command payload that will be recieved by the API
class CommandPayload(BaseModel):
    intent: IntentType = Field(..., description="The intent of the command")
    query: str = Field(..., description="The command to be executed")
    confidence : float = Field(..., ge=0.0, le=1.0, description="Confidence score of the intent classification (0.0 to 1.0)")