from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)   #Create app instance
cors = CORS(app, origins='*')

@app.route("/api/users", methods=['GET'])
def users():
    return jsonify(
        { 
            "users": [
                'kent',
                'rachel',
                'test',
                'test'
            ]
        }
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)