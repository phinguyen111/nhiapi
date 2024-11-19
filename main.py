from flask import Flask, jsonify, request
from flask_cors import CORS
from database_connection import connect_to_neo4j  # Hàm kết nối tới Neo4j
from etherscan_to_neo4j import fetch_and_save_transactions  # Hàm xử lý giao dịch từ Etherscan
from dotenv import load_dotenv
import os

# Load các biến môi trường từ .env
load_dotenv()

# Khởi tạo Flask app
app = Flask(__name__)
# Cấu hình CORS để cho phép kết nối từ Frontend
CORS(app, resources={r"/*": {"origins": "https://6h54fix.vercel.app"}})
# Kết nối với cơ sở dữ liệu Neo4j
neo4j_driver = connect_to_neo4j(
    os.getenv("NEO4J_URI"), 
    os.getenv("NEO4J_USER"), 
    os.getenv("NEO4J_PASSWORD")
)

# Định nghĩa endpoint /api/transactions
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Lấy tham số "address" từ URL
    address = request.args.get('address')
    if not address:
        # Nếu không có địa chỉ, trả về lỗi
        return jsonify({"error": "Address is required"}), 400

    try:
        # Gọi hàm fetch_and_save_transactions để lấy dữ liệu giao dịch
        transactions = fetch_and_save_transactions(address)

        # Trả về dữ liệu giao dịch dưới dạng JSON
        return jsonify({"success": True, "transactions": transactions})
    except Exception as e:
        # Xử lý lỗi nếu xảy ra
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Chạy server Flask trên localhost
    app.run(debug=True, port=5001)
