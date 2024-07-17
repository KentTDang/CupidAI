from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from planner import DatePlanner
import uuid

app = Flask(__name__)
CORS(app, origins='*')

# Create an instance of the DatePlanner
response_instance = DatePlanner()

# Initialize a unique thread ID for each conversation
thread = {"configurable": {"thread_id": uuid.uuid4()}}

@app.route("/api/cupid-ai", methods=['GET', 'POST'])
def get_date_plan():
    task = 'Generate a date plan in Maryland'
    if request.method == 'POST':
        input_data = request.data.decode('utf-8')
        task = json.loads(input_data).get("task", task)
    result = []
    for state in response_instance.graph.stream({
        'task': task,
        'max_revisions': 2,
        'revision_number': 1,
    }, thread):
        result.append(state)
    return jsonify(result)
