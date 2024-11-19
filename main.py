from flask import Flask, jsonify, request
from flask_cors import CORS
from database_connection import connect_to_neo4j  # Import your database connection function
from etherscan_to_neo4j import fetch_and_save_transactions  # Import for interacting with Etherscan API

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend integration

# Setup Neo4j connection
neo4j_driver = connect_to_neo4j("neo4j+s://aadff3f9.databases.neo4j.io", "neo4j", "TVuvrmUqxBe3u-gDv6oISHDlZKLxUJKz3q8FrOXyWmo")

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400

    # Fetch transaction data and save to Neo4j
    transactions = fetch_and_save_transactions(address)
    
    # Return transactions as JSON response
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Local development port
