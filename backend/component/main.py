from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from flask import Flask, jsonify
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Check if TAVILY_API_KEY is set
api_key = os.getenv("TAVILY_API_KEY")
if api_key is None:
    raise ValueError("TAVILY_API_KEY environment variable is not set")

# Initialize the model
try:
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    print("Model initialized successfully gyat.")
except Exception as e:
    print("Error initializing model:", str(e))

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route("/api/test", methods=['GET'])
def test():
    return jsonify({
        "status": "success",
        # "model": model,
        
        
    })

if __name__ == "__main__":
    app.run(debug=True, port=8080)
