from openenv.core.env_server.types import Action, Observation
from pydantic import Field

class SqlQueryAction(Action):
    query: str = Field(..., description="SQL query to execute")

class SqlQueryObservation(Observation):
    task_id: str = Field(default="")
    difficulty: str = Field(default="")
    description: str = Field(default="")
    schema_hint: str = Field(default="")
    result: str = Field(default="")
    reward: float = Field(default=0.0)
    done: bool = Field(default=False)
    feedback: str = Field(default="")