from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from models import SqlQueryAction, SqlQueryObservation

class SqlQueryEnv(EnvClient[SqlQueryAction, SqlQueryObservation, State]):

    def _step_payload(self, action: SqlQueryAction) -> Dict:
        return {"query": action.query}

    def _parse_result(self, payload: Dict) -> StepResult[SqlQueryObservation]:
        obs_data = payload.get("observation", {})
        observation = SqlQueryObservation(
            task_id=obs_data.get("task_id", ""),
            difficulty=obs_data.get("difficulty", ""),
            description=obs_data.get("description", ""),
            schema_hint=obs_data.get("schema_hint", ""),
            result=obs_data.get("result", ""),
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
            feedback=obs_data.get("feedback", ""),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )