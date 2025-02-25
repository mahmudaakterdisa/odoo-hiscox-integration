from flask import Flask, request, jsonify

app = Flask(__name__)

db = {}

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    email = data.get("email")
    db[email] = {"status": "submitted"}
    return jsonify({"message": "Application submitted"}), 200

@app.route('/status', methods=['GET'])
def status():
    email = request.args.get("email")
    return jsonify({"status": db.get(email, {}).get("status", "pending")}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
