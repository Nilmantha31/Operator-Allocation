from .worker import celery_app
from flask import Flask
from .blueprints.opAutoAllocation_bp import opAutoAllocationBp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

flask_app = app

celery = celery_app

app.register_blueprint(opAutoAllocationBp, url_prefix='/api')

