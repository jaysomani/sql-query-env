from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SqlQueryAction, SqlQueryObservation
except ImportError:
    from models import SqlQueryAction, SqlQueryObservation

from server.tasks import TASKS
from server.grader import grade
from server.db import get_db

class SqlQueryEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.tasks = TASKS
        self.current_task_index = 0

    def reset(self, task_index: int = 0) -> SqlQueryObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_index = task_index
        task = self.tasks[task_index]
        return SqlQueryObservation(
            task_id=task["task_id"],
            difficulty=task["difficulty"],
            description=task["description"],
            schema_hint=task["schema_hint"],
            result="",
            reward=0.0,
            done=False,
            feedback="Episode started. Write a SQL query to solve the task."
        )

    def step(self, action: SqlQueryAction) -> SqlQueryObservation:
        self._state.step_count += 1

        # handle task navigation BEFORE any SQL execution
        if action.query.startswith("__set_task__:"):
            task_index = int(action.query.split(":")[1])
            self.current_task_index = task_index
            task = self.tasks[task_index]
            return SqlQueryObservation(
                task_id=task["task_id"],
                difficulty=task["difficulty"],
                description=task["description"],
                schema_hint=task["schema_hint"],
                result="",
                reward=0.0,
                done=False,
                feedback=f"Switched to task {task_index}. Write a SQL query to solve the task."
            )

        task = self.tasks[self.current_task_index]
        reward = grade(action.query, task["expected_output"])

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(action.query)
            rows = cursor.fetchall()
            result_str = str(rows[:5])
            conn.close()
        except Exception as e:
            result_str = f"Error: {str(e)}"

        is_last = self.current_task_index >= len(self.tasks) - 1
        if reward >= 0.5 and not is_last:
            self.current_task_index += 1

        done = is_last and reward >= 0.5

        feedback = (
            "Correct!" if reward == 1.0 else
            "Partial match, close but not exact." if reward > 0 else
            "Incorrect. Check your query and try again."
        )

        next_task = self.tasks[self.current_task_index]
        return SqlQueryObservation(
            task_id=next_task["task_id"],
            difficulty=next_task["difficulty"],
            description=next_task["description"],
            schema_hint=next_task["schema_hint"],
            result=result_str,
            reward=reward,
            done=done,
            feedback=feedback
        )

    @property
    def state(self) -> State:
        return self._state