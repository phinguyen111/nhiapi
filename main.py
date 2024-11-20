from flask import Flask, jsonify, request, make_response
from database_connection import connect_to_neo4j
from etherscan_to_neo4j import fetch_and_save_transactions
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

# Cập nhật cấu hình CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://6h54fix.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Kết nối Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://aadff3f9.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    neo4j_driver = connect_to_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    print("Connected to Neo4j successfully!")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")

# Middleware CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://6h54fix.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API is running!"})

@app.route('/api/transactions', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'https://6h54fix.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({"error": "Address is required"}), 400

        transactions = fetch_and_save_transactions(address)
        
        # Format transactions
        formatted_transactions = []
        for tx in transactions:
            if float(tx.get('amount', 0)) > 0:
                formatted_tx = {
                    'from': tx['from'],
                    'to': tx['to'],
                    'amount': float(tx['amount']),
                    'timestamp': int(tx['timeStamp']),
                    'hash': tx.get('hash'),
                    'block': tx.get('blockNumber'),
                    'fee': tx.get('gasUsed', '0.000000')
                }
                formatted_transactions.append(formatted_tx)

        response = jsonify({
            "success": True,
            "transactions": formatted_transactions
        })
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)