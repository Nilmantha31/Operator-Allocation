from flask import Blueprint
from flask import jsonify, request, abort
from .tasks.opAutoAllocation_task import opAutoAllocation_task

opAutoAllocationBp = Blueprint('opAutoAllocationBp', __name__)

@opAutoAllocationBp.route('/')
def index():
    return 'Welcome! App is running'


@opAutoAllocationBp.route("/opAutoAllocation", methods=['POST'])
def opAutoAllocation():

    if not request.is_json:
        abort(400, description="Request must be JSON.")

    try:
        request_data = request.get_json()
        task = opAutoAllocation_task.apply_async(args=[request_data])

        result = task.get()

        return jsonify({"result": result}), 200

    except Exception as e:
        abort(500, description="Internal error while processing the task.")