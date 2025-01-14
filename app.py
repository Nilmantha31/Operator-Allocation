from flask import Flask, jsonify, request
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

app = Flask(__name__)

@app.route('/', methods=['POST'])
def optimize():
    request_data = request.get_json()

    # Parse input data
    machines = {m["machine_id"]: m["operation_ids"] for m in request_data["machines"]}
    operations = {
        detail["operation_id"]: {
            "performing_time": detail["performing_time"],
            "smv": detail["smv"]
        }
        for detail in request_data["operation_details"]
    }
    operators = {
        op["operator_id"]: op["efficiency"] for op in request_data["operators"]
    }

    # Define the optimization problem
    problem = LpProblem("Maximize_Bottleneck_Output", LpMaximize)

    # Decision variables: binary variables for machine-operator assignments
    x = {
        (m, o): LpVariable(f"x_{m}_{o}", cat="Binary")
        for m in machines
        for o in operators
    }

    # Continuous variable for bottleneck (minimum output)
    z = LpVariable("z", lowBound=0, cat="Continuous")

    outputs = {}
    machine_outputs = {}

    # Calculate outputs for each operation
    for op_id, op_data in operations.items():
        op_performing_time = op_data["performing_time"]
        op_smv = op_data["smv"]

        # Output for each operation is the sum of contributions by all machines and operators
        outputs[op_id] = lpSum(
            x[m, o] * op_performing_time * operators[o].get(str(op_id), 0) / op_smv
            for m in machines if op_id in machines[m]
            for o in operators
        )

        for m in machines:
            if op_id in machines[m]:
                machine_outputs[m] = lpSum(
                    x[m, o]
                    * (op_performing_time / 60)
                    * operators[o].get(str(op_id), 0)
                    / op_smv
                    for o in operators
                )

    # Objective: Maximize the bottleneck (minimum output across operations)
    problem += z, "Maximize_Bottleneck"

    # Constraints: Ensure z is less than or equal to each operation's output
    for op_id, output in outputs.items():
        problem += z <= output, f"Constraint_Bottleneck_{op_id}"

    # Constraints: Each machine must have exactly one operator
    for m in machines:
        problem += lpSum(x[m, o] for o in operators) == 1

    # Constraints: Each operator can operate at most one machine
    for o in operators:
        problem += lpSum(x[m, o] for m in machines) <= 1

    problem.solve()

    # Extract assignments and outputs
    assignments = {}
    hourly_outputs = {}
    for m in machines:
        for o in operators:
            if value(x[m, o]) > 0.5:
                if value(machine_outputs.get(m, 0)) > 0:
                    assignments[m] = o

    for op_id, output in outputs.items():
        hourly_outputs[op_id] = value(output)

    # Determine the bottleneck value
    bottleneck_value = value(z)

    result = {
        "assignments": assignments,
        "bottleneck_value": bottleneck_value,
        "outputs": hourly_outputs
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='192.168.40.129', debug=True, port=5000)
