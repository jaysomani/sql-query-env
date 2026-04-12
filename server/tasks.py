TASKS = [
    {
        "task_id": "task_easy",
        "difficulty": "easy",
        "description": "Find the names and cities of all customers who joined in 2021 or later.",
        "schema_hint": "Table: customers(id, name, city, joined_year)",
        "expected_output": [("Alice", "Mumbai"), ("Charlie", "Bangalore")],
    },
    {
        "task_id": "task_medium",
        "difficulty": "medium",
        "description": "Find the name of each customer and the total number of orders they have placed. Only include customers who have placed at least 2 orders.",
        "schema_hint": "Tables: customers(id, name, city, joined_year), orders(id, customer_id, product_id, quantity, order_date)",
        "expected_output": [("Alice", 2), ("Bob", 2)],
    },
    {
        "task_id": "task_hard",
        "difficulty": "hard",
        "description": "Find the total revenue (price * quantity) generated per product category. Return category and total_revenue, sorted by total_revenue descending.",
        "schema_hint": "Tables: products(id, name, category, price), orders(id, customer_id, product_id, quantity, order_date)",
        "expected_output": [("Electronics", 225000.0), ("Clothing", 10500.0)],
    },
]