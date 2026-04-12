---
title: SQL Query Environment
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
tags:
  - openenv
  - rl
  - sql
---

# SQL Query RL Environment

A reinforcement learning environment where an AI agent learns to write correct SQLite queries across 3 difficulty levels using an e-commerce database schema.

## Environment Description

The agent is given a natural language task description and a database schema hint. It must write a valid SQLite query that returns the correct result. Rewards are based on output correctness.

### Database Schema
- `customers(id, name, city, joined_year)`
- `products(id, name, category, price)`
- `orders(id, customer_id, product_id, quantity, order_date)`

### Tasks
- **Easy**: Single table SELECT with WHERE clause
- **Medium**: JOIN across 2 tables with GROUP BY and HAVING
- **Hard**: Multi-table JOIN with aggregation and ORDER BY

### Reward Function
- `1.0` — exact match
- `0.0–0.5` — partial match (some rows correct)
- `0.0` — incorrect or error

## Action Space
`SqlQueryAction` — contains a single field:
- `query` (str) — the SQL query to execute

## Observation Space
`SqlQueryObservation` — contains:
- `task_id` (str) — current task identifier
- `difficulty` (str) — easy / medium / hard
- `description` (str) — natural language task description
- `schema_hint` (str) — relevant table schemas
- `result` (str) — query result or error message
- `reward` (float) — score for last action
- `done` (bool) — episode completion flag
- `feedback` (str) — human readable feedback

## Quick Start

```python
from client import SqlQueryEnv, SqlQueryAction

with SqlQueryEnv(base_url="https://YOUR_SPACE_URL").sync() as env:
    result = env.reset()
    obs = result.observation
    print(obs.description)
    
    step = env.step(SqlQueryAction(query="SELECT name, city FROM customers WHERE joined_year >= 2021"))
    print(step.reward)  # 1.0 if correct
```

## Running Locally

```bash
pip install openenv-core fastapi uvicorn pydantic
uvicorn server.app:app --host 0.0.0.0 --port 7860
```