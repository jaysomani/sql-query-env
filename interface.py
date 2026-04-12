import os
import json
from openai import OpenAI
from sql_query_env import SQLAction, SQLQueryEnv  # your client class

API_BASE_URL = os.environ["API_BASE_URL"]
MODEL_NAME = os.environ["MODEL_NAME"]
HF_SPACE_URL = os.environ.get("HF_SPACE_URL", "http://localhost:8000")

client = OpenAI(base_url=API_BASE_URL, api_key=os.environ.get("HF_TOKEN", "x"))

def ask_llm(description, schema_hint, feedback, prev_result):
    prompt = f"""You are a SQL expert. Write a single valid SQLite query.

Task: {description}
Schema: {schema_hint}
Previous result: {prev_result}
Feedback: {feedback}

Respond with ONLY the SQL query, nothing else."""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

with SQLQueryEnv(base_url=HF_SPACE_URL).sync() as env:
    from server.tasks import TASKS
    
    for task in TASKS:
        obs = env.reset()
        total_reward = 0.0
        
        print(json.dumps({"type": "[START]", "task_id": task["task_id"], "difficulty": task["difficulty"]}))
        
        for step_num in range(3):  # max 3 attempts per task
            query = ask_llm(
                obs.description,
                obs.schema_hint,
                obs.feedback,
                obs.result
            )
            
            action = SQLAction(query=query)
            obs = env.step(action)
            total_reward = obs.reward
            
            print(json.dumps({
                "type": "[STEP]",
                "step": step_num + 1,
                "action": query,
                "observation": obs.result,
                "reward": obs.reward,
                "done": obs.done
            }))
            
            if obs.done or obs.reward == 1.0:
                break
        
        print(json.dumps({"type": "[END]", "task_id": task["task_id"], "total_reward": total_reward}))