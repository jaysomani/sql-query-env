import os
import json
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-api-base-url>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model-name>")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "http://localhost:7860")

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

def reset_env(task_index=0):
    r = requests.post(f"{HF_SPACE_URL}/reset", json={"task_index": task_index})
    return r.json()

def step_env(query):
    r = requests.post(
        f"{HF_SPACE_URL}/step",
        json={"action": {"query": query}}
    )
    return r.json()

TASKS = [
    {
        "task_id": "task_easy",
        "difficulty": "easy",
        "description": "Find the names and cities of all customers who joined in 2021 or later.",
        "schema_hint": "Table: customers(id, name, city, joined_year)",
    },
    {
        "task_id": "task_medium",
        "difficulty": "medium",
        "description": "Find the name of each customer and the total number of orders they have placed. Only include customers who have placed at least 2 orders.",
        "schema_hint": "Tables: customers(id, name, city, joined_year), orders(id, customer_id, product_id, quantity, order_date)",
    },
    {
        "task_id": "task_hard",
        "difficulty": "hard",
        "description": "Find the total revenue (price * quantity) generated per product category. Return category and total_revenue, sorted by total_revenue descending.",
        "schema_hint": "Tables: products(id, name, category, price), orders(id, customer_id, product_id, quantity, order_date)",
    },
]

for i, task in enumerate(TASKS):
    try:
        obs_data = reset_env(task_index=i)
        obs = obs_data["observation"]

        print(json.dumps({
            "type": "[START]",
            "task_id": task["task_id"],
            "difficulty": task["difficulty"]
        }))

        total_reward = 0.0

        for step_num in range(3):
            try:
                query = ask_llm(
                    task["description"],
                    task["schema_hint"],
                    obs.get("feedback", ""),
                    obs.get("result", "")
                )

                result = step_env(query)
                obs = result["observation"]
                reward = result["reward"]
                done = result["done"]
                total_reward = reward

                print(json.dumps({
                    "type": "[STEP]",
                    "step": step_num + 1,
                    "action": query,
                    "observation": obs.get("result", ""),
                    "reward": reward,
                    "done": done
                }))

                if done or reward == 1.0:
                    break

            except Exception as e:
                print(json.dumps({
                    "type": "[STEP]",
                    "step": step_num + 1,
                    "action": "",
                    "observation": f"Error: {str(e)}",
                    "reward": 0.0,
                    "done": False
                }))

        print(json.dumps({
            "type": "[END]",
            "task_id": task["task_id"],
            "total_reward": total_reward
        }))

    except Exception as e:
        print(json.dumps({
            "type": "[END]",
            "task_id": task["task_id"],
            "total_reward": 0.0
        }))