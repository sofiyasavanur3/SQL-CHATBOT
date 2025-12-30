# SQL Chatbot (Natural Language → SQL)

A production-ready SQL chatbot that allows users to ask questions in plain English and get answers directly from a relational database.  
The system converts natural language into safe, read-only SQL queries and executes them on a local SQLite database.

---

## Why this project exists

Business users often need answers from databases but do not know SQL.  
This project removes that barrier by letting users ask questions in natural language while keeping full control over database access and query safety.

---

## What this project does

- Converts natural language questions into SQL
- Executes queries on a local SQLite database
- Returns tabular results and a human-readable explanation
- Prevents write operations (SELECT-only enforcement)
- Runs as a web application

---

## Tech stack

- **Backend**: Python, Flask
- **Database**: SQLite (Northwind sample database)
- **LLM**: OpenAI API (SQL generation + result explanation)
- **Frontend**: HTML, CSS, vanilla JavaScript
- **Deployment-ready**: Gunicorn compatible

---

## System architecture

User Question
↓
Frontend (HTML + JS)
↓
Flask API
↓
LLM (Natural Language → SQL)
↓
SQLite Database
↓
Query Results
↓
LLM (Results → Natural Language)
↓
User Answer


Key design decision:

- The LLM **never connects to the database directly**
- All SQL is executed by controlled backend logic


## Database

- **Engine**: SQLite
- **Schema**: Northwind Traders
- **Tables include**:
  - Customers
  - Orders
  - Order Details
  - Products
  - Suppliers
  - Categories
  - Shippers

The database is included to allow instant local execution without setup.

---

## Features

- Natural language to SQL conversion
- Automatic JOIN handling
- Aggregate queries (COUNT, SUM, AVG)
- Result table rendering
- Plain-English answer generation
- Sample questions for guided exploration
- Read-only query enforcement

---
Key design decision:
- The LLM **never connects to the database directly**
- All SQL is executed by controlled backend logic

---

## Local setup

1. Clone repository

```bash
git clone https://github.com/sofiyasavnur3/SQL-CHATBOT.git
cd SQL-CHATBOT


2. Create virtual environment
bash
Copy code
python3 -m venv venv
source venv/bin/activate


3. Install dependencies
bash
Copy code
pip install -r requirements.txt


4. Configure environment variables
Create a .env file:

text
Copy code
OPENAI_API_KEY=your_api_key_here
.env is intentionally excluded from Git for security reasons.

5. Run the app
bash
Copy code
python app.py
Open in browser:

arduino
Copy code
http://localhost:5000


Security considerations

.env is excluded from version control
OpenAI API key is loaded via environment variables
Only SELECT queries are allowed
No user input is executed directly as SQL
Database access is isolated to backend

Limitations
SQLite is single-user and not designed for heavy concurrency
Query accuracy depends on schema description quality
No authentication or authorization (intentionally out of scope)
Not optimized for very large datasets


Future improvements
Automatic schema introspection (no hardcoded schema)
SQL query validation layer
Pagination and result limits
Authentication and role-based access
Dockerized deployment
Support for PostgreSQL / MySQL
Streaming responses for large result sets


Why this project matters
This project demonstrates:
Practical GenAI usage beyond demos
Safe LLM integration with structured dat
Backend system design thinking
Security-aware development
Deployment-ready Flask architecture

It reflects real-world patterns used in internal analytics tools and enterprise assistants.

Author
Sofiya Savnur
Data Scientist | ML & Generative AI
GitHub: https://github.com/sofiyasavnur3