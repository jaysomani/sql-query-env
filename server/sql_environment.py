from openenv.core.environment import Environment
from models import SQLAction, SQLObservation
from server.tasks import TASKS
from server.grader import grade

class SQLQueryEnvironment(Environment):
    def __init__(self):
        self.tasks = TASKS
        self.current_task_index = 0
        self.episode_id = None

    def reset(self) -> SQLObservation:
        self.current_task_index = 0
        task = self.tasks[0]
        return SQLObservation(
            task_id=task["task_id"],
            difficulty=task["difficulty"],
            description=task["description"],
            schema_hint=task["schema_hint"],
            result="",
            reward=0.0,
            done=False,
            feedback="New episode started. Solve the task using SQL."
        )

    def step(self, action: SQLAction) -> SQLObservation:
        task = self.tasks[self.current_task_index]
        reward = grade(action.query, task["expected_output"])

        # try to get actual query result for observation
        try:
            from server.db import get_db
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(action.query)
            rows = cursor.fetchall()
            result_str = str(rows[:5])  # show first 5 rows
            conn.close()
        except Exception as e:
            result_str = f"Error: {str(e)}"

        # move to next task if reward > 0, or it's the last task
        is_last = self.current_task_index >= len(self.tasks) - 1
        if reward >= 0.5 or is_last:
            done = is_last
            if not is_last:
                self.current_task_index += 1
        else:
            done = False

        feedback = "Correct!" if reward == 1.0 else (
            "Partial match." if reward > 0 else "Incorrect. Try again."
        )

        next_task = self.tasks[self.current_task_index]
        return SQLObservation(
            task_id=next_task["task_id"],
            difficulty=next_task["difficulty"],
            description=next_task["description"],
            schema_hint=next_task["schema_hint"],
            result=result_str,
            reward=reward,
            done=done,
            feedback=feedback
        )

    def state(self):
        return {
            "current_task_index": self.current_task_index,
            "total_tasks": len(self.tasks)
        }