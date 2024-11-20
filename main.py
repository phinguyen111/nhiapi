from flask import Flask, jsonify, request, make_response
from database_connection import connect_to_neo4j  # Hàm kết nối tới Neo4j
from etherscan_to_neo4j import fetch_and_save_transactions  # Hàm xử lý giao dịch từ Etherscan
from dotenv import load_dotenv
import os
import time
from flask_cors import CORS
import logging

# Load các biến môi trường từ .env
load_dotenv()

# Khởi tạo Flask app
app = Flask(__name__)

# Kích hoạt CORS
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG)

# Kết nối với Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://aadff3f9.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    neo4j_driver = connect_to_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    logging.info("Connected to Neo4j successfully!")
except Exception as e:
    logging.error(f"Failed to connect to Neo4j: {e}")

# Middleware thêm tiêu đề CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Route chính để kiểm tra API
@app.route('/', methods=['GET'])
def home():
    """Root route to verify API is running."""
    return jsonify({"message": "API is running!"})

# Route lấy danh sách giao dịch từ Etherscan
@app.route('/api/transactions', methods=['GET', 'OPTIONS'])
def get_transactions():
    """Fetch transactions for a given address."""
    if request.method == 'OPTIONS':
        # Phản hồi preflight request
        response = make_response(jsonify({"message": "Preflight request successful"}))
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    start_time = time.time()  # Bắt đầu theo dõi thời gian xử lý

    try:
        address = request.args.get('address')
        if not address:
            return jsonify({"error": "Address is required"}), 400

        # Fetch transaction data and save to Neo4j
        transactions = fetch_and_save_transactions(address)
        processing_time = time.time() - start_time  # Kết thúc theo dõi
        logging.info(f"Processed {len(transactions)} transactions for address {address} in {processing_time:.2f} seconds")

        # Return transactions as JSON response
        return jsonify({"success": True, "transactions": transactions}), 200

    except Exception as e:
        # Xử lý lỗi nếu xảy ra
        logging.error(f"Error processing request for address {address}: {e}")
        return jsonify({"error": str(e)}), 500

# Xử lý lỗi không xác định
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled error: {e}")
    return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    # Chạy server Flask
    app.run(debug=True, host="0.0.0.0", port=5001)
