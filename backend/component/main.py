from flask import Flask, jsonify

app = Flask(__name__)   #Create app instance

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