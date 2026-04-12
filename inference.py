import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from client import SqlQueryEnv
from models import SqlQueryAction
from server.tasks import TASKS

API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-api-base-url>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model-name>")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.environ.get("HF_SPACE_URL", "http://localhost:8000")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def ask_llm(description, schema_hint, feedback, prev_result):
    prompt = f"""You are a SQL expert. Write a single valid SQLite query to solve the task.

Task: {description}
Schema: {schema_hint}
Previous result: {prev_result}
Feedback: {feedback}

Respond with ONLY the raw SQL query, no explanation, no markdown, no backticks."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

with SqlQueryEnv(base_url=HF_SPACE_URL).sync() as env:
    for i, task in enumerate(TASKS):
        # reset and jump to correct task via set_task step
        result = env.reset()
        
        # navigate to the right task index
        if i > 0:
            nav_result = env.step(SqlQueryAction(query=f"__set_task__:{i}"))
            obs = nav_result.observation
        else:
            obs = result.observation

        print(json.dumps({
            "type": "[START]",
            "task_id": task["task_id"],
            "difficulty": task["difficulty"]
        }))

        total_reward = 0.0

        for step_num in range(3):
            query = ask_llm(
                task["description"],
                task["schema_hint"],
                obs.feedback,
                obs.result
            )

            step_result = env.step(SqlQueryAction(query=query))
            obs = step_result.observation
            reward = step_result.reward
            done = step_result.done
            total_reward = reward

            print(json.dumps({
                "type": "[STEP]",
                "step": step_num + 1,
                "action": query,
                "observation": obs.result,
                "reward": reward,
                "done": done
            }))

            if done or reward == 1.0:
                break

        print(json.dumps({
            "type": "[END]",
            "task_id": task["task_id"],
            "total_reward": total_reward
        }))