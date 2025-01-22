from .worker import celery_app
from flask import Flask, jsonify
from .blueprints.opAutoAllocation_bp import opAutoAllocationBp

app = Flask(__name__)

flask_app = app

celery = celery_app

app.register_blueprint(opAutoAllocationBp, url_prefix='/api')

