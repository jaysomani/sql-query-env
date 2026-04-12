import sqlite3

def get_db():
    conn = sqlite3.connect(":memory:")  # in-memory, fresh per episode
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            joined_year INTEGER
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TEXT
        );
        
        INSERT INTO customers VALUES (1,'Alice','Mumbai',2021);
        INSERT INTO customers VALUES (2,'Bob','Delhi',2020);
        INSERT INTO customers VALUES (3,'Charlie','Bangalore',2022);
        INSERT INTO customers VALUES (4,'Diana','Mumbai',2019);

        INSERT INTO products VALUES (1,'Laptop','Electronics',75000);
        INSERT INTO products VALUES (2,'Phone','Electronics',25000);
        INSERT INTO products VALUES (3,'Shirt','Clothing',1500);
        INSERT INTO products VALUES (4,'Shoes','Clothing',3000);

        INSERT INTO orders VALUES (1,1,1,1,'2024-01-15');
        INSERT INTO orders VALUES (2,1,2,2,'2024-02-10');
        INSERT INTO orders VALUES (3,2,3,3,'2024-01-20');
        INSERT INTO orders VALUES (4,3,1,1,'2024-03-05');
        INSERT INTO orders VALUES (5,4,4,2,'2024-02-28');
        INSERT INTO orders VALUES (6,2,2,1,'2024-03-10');
    """)
    conn.commit()
    return conn