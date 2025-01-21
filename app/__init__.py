from .worker import celery_app
from flask import Flask, jsonify
from .blueprints.opAutoAllocation_task import sum

app = Flask(__name__)

flask_app = app

celery = celery_app

@app.route('/')
def sumtask():
    task = sum.apply_async()
    result = task.get()
    return jsonify(result)

