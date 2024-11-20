from flask import Flask, jsonify, request, make_response
from database_connection import connect_to_neo4j  # Hàm kết nối tới Neo4j
from etherscan_to_neo4j import fetch_and_save_transactions  # Hàm xử lý giao dịch từ Etherscan
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Load các biến môi trường từ .env
load_dotenv()

# Khởi tạo Flask app
app = Flask(__name__)

# CORS config: Chỉ cho phép domain cụ thể
CORS(app, resources={r"/*": {"origins": "https://6h54fix.vercel.app"}})

# Kết nối với Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://aadff3f9.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    neo4j_driver = connect_to_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    print("Connected to Neo4j successfully!")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")

# Middleware thêm tiêu đề CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/', methods=['GET'])
def home():
    """Root route to verify API is running."""
    return jsonify({"message": "API is running!"})

@app.route('/api/address/<address>/transactions', methods=['GET'])
def get_address_transactions(address):
    """
    Lấy danh sách giao dịch của một địa chỉ từ Etherscan và xử lý.
    """
    api_key = os.getenv('ETHERSCAN_API_KEY')  # Lấy API key từ biến môi trường
    if not api_key:
        return jsonify({"error": "ETHERSCAN_API_KEY not found in environment variables"}), 500

    try:
        # Lấy dữ liệu giao dịch từ Etherscan
        transactions = fetch_and_save_transactions(address)
        if not transactions:
            return jsonify({"error": "No transactions found for this address"}), 404

        # Xử lý dữ liệu giao dịch thành cấu trúc cần thiết
        tx_data = []
        for tx in transactions:
            txn_fee = int(tx['gasUsed']) * int(tx['gasPrice']) / 10**18
            tx_data.append({
                "hash": tx['hash'],
                "block": tx['blockNumber'],
                "from": tx['from'],
                "to": tx['to'],
                "amount": f"{int(tx['value']) / 10**18:.8f} ETH",
                "fee": f"{txn_fee:.8f}"
            })

        # Trả về danh sách giao dịch
        return jsonify({"success": True, "transactions": tx_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


