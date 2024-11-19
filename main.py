from flask import Flask, jsonify, request
from flask_cors import CORS
from database_connection import connect_to_neo4j  # Import your database connection function
from etherscan_to_neo4j import fetch_and_save_transactions  # Import for interacting with Etherscan API
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app) 

# Setup Neo4j connection using environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://aadff3f9.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    neo4j_driver = connect_to_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    print("Connected to Neo4j successfully!")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")

@app.route('/', methods=['GET'])
def home():
    """Root route to verify API is running."""
    return jsonify({"message": "API is running!"})

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400

    try:
        # Fetch transaction data
        transactions = fetch_and_save_transactions(address)
        return jsonify({"success": True, "transactions": transactions})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Local development port
