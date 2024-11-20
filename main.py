from flask import Flask, jsonify, request, make_response
from database_connection import connect_to_neo4j
from etherscan_to_neo4j import fetch_and_save_transactions
from dotenv import load_dotenv
import os

# Load các biến môi trường từ .env
load_dotenv()

# Khởi tạo Flask app
app = Flask(__name__)

# Kết nối với Neo4j
neo4j_driver = connect_to_neo4j(
    os.getenv("NEO4J_URI"), 
    os.getenv("NEO4J_USER"), 
    os.getenv("NEO4J_PASSWORD")
)

# Định nghĩa middleware để thêm tiêu đề CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "https://6h54fix.vercel.app"  # Thay bằng URL của frontend bạn
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Endpoint /api/transactions
@app.route('/api/transactions', methods=['GET', 'OPTIONS'])
def get_transactions():
    if request.method == 'OPTIONS':
        # Trả về phản hồi cho OPTIONS request
        response = make_response(jsonify({"message": "Preflight request successful"}))
        response.headers["Access-Control-Allow-Origin"] = "https://6h54fix.vercel.app"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400

    try:
        transactions = fetch_and_save_transactions(address)
        return jsonify({"success": True, "transactions": transactions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
