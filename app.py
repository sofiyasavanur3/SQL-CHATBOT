"""
SQL Chatbot Web Application
A Flask web app that converts natural language to SQL queries
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database schema for the AI to understand
DATABASE_SCHEMA = """
Database: Northwind (SQLite)

Tables:
1. Customers (CustomerID, CompanyName, ContactName, City, Country)
2. Suppliers (SupplierID, CompanyName, ContactName, City, Country)
3. Products (ProductID, ProductName, SupplierID, UnitPrice, Discontinued)
4. Orders (OrderID, CustomerID, OrderDate, ShipCity, ShipCountry)
5. "Order Details" (OrderID, ProductID, UnitPrice, Quantity, Discount)
6. Categories (CategoryID, CategoryName)
7. Shippers (ShipperID, CompanyName)

Relationships:
- Customers.CustomerID → Orders.CustomerID
- Suppliers.SupplierID → Products.SupplierID
- Products.ProductID → "Order Details".ProductID
- Orders.OrderID → "Order Details".OrderID
- Categories.CategoryID → Products.CategoryID
"""


def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('northwind.db')
    conn.row_factory = sqlite3.Row
    return conn


def execute_sql(sql_query):
    """Execute SQL query and return results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        conn.close()
        
        return {
            'success': True,
            'columns': columns,
            'rows': results,
            'row_count': len(results)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_sql_from_question(question):
    """Use OpenAI to convert natural language to SQL"""
    
    system_prompt = f"""You are a SQL expert. Convert user questions into SQL queries for SQLite.

{DATABASE_SCHEMA}

Rules:
1. Generate ONLY SELECT queries (read-only)
2. Use SQLite syntax
3. Table name for orders is [Order] (with brackets)
4. Return ONLY the SQL query, no explanations
5. Limit results to 100 rows unless asked otherwise
6. Use proper JOINs when querying multiple tables
7. Use aggregate functions (COUNT, SUM, AVG) when appropriate
8. If a table name contains spaces, wrap it in double quotes

Examples:
Q: "How many customers are there?"
A: SELECT COUNT(*) as total_customers FROM Customer;

Q: "Show me all products with their suppliers"
A: SELECT p.ProductName, p.UnitPrice, s.CompanyName as Supplier 
   FROM Product p 
   JOIN Supplier s ON p.SupplierId = s.Id 
   LIMIT 100;
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return {
            'success': True,
            'sql': sql_query
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_natural_language_response(question, sql_query, query_results):
    """Use OpenAI to explain the results in natural language"""
    
    if not query_results['success']:
        return "I encountered an error executing the query."
    
    row_count = query_results['row_count']
    
    if row_count == 0:
        results_summary = "No results found."
    else:
        sample_rows = query_results['rows'][:5]
        results_summary = f"Found {row_count} rows. First few results:\n"
        for row in sample_rows:
            results_summary += f"{row}\n"
        
        if row_count > 5:
            results_summary += f"... and {row_count - 5} more rows."
    
    prompt = f"""Question: {question}
SQL Query: {sql_query}
Results: {results_summary}

Provide a clear, concise natural language answer to the user's question based on these results. 
Be specific and include relevant numbers or details."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains database query results clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating response: {str(e)}"


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    """Handle user questions and return SQL + results"""
    
    data = request.json
    user_question = data.get('question', '').strip()
    
    if not user_question:
        return jsonify({'error': 'Please enter a question'}), 400
    
    sql_result = generate_sql_from_question(user_question)
    
    if not sql_result['success']:
        return jsonify({
            'error': f"Error generating SQL: {sql_result['error']}"
        }), 500
    
    sql_query = sql_result['sql']
    query_results = execute_sql(sql_query)
    
    if query_results['success']:
        nl_response = generate_natural_language_response(
            user_question, 
            sql_query, 
            query_results
        )
    else:
        nl_response = f"Error executing query: {query_results['error']}"
    
    return jsonify({
        'question': user_question,
        'sql': sql_query,
        'results': query_results,
        'answer': nl_response
    })


@app.route('/sample-questions', methods=['GET'])
def sample_questions():
    """Return sample questions users can ask"""
    samples = [
        "How many customers do we have?",
        "Show me all products",
        "List customers from London",
        "What's the total value of all orders?",
        "Show me the most expensive products",
        "Which customer has placed the most orders?",
        "List all products from Tokyo Traders",
        "Show me orders from January 2024",
        "What's the average order value?",
        "List all suppliers and their cities"
    ]
    return jsonify({'samples': samples})


if __name__ == '__main__':
    if not os.path.exists('northwind.db'):
        print("\n⚠️  WARNING: Database not found!")
        print("📝 Run 'python setup_database.py' first to create the database.\n")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OpenAI API key not found!")
        print("📝 Create a .env file with: OPENAI_API_KEY=your-key-here\n")
    
    print("\n" + "="*60)
    print("🚀 SQL CHATBOT SERVER STARTING")
    print("="*60)
    print("\n📱 Open your browser and go to: http://localhost:5000")
    print("\n💡 Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)