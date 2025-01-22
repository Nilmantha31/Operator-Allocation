from ...worker import celery_app
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

@celery_app.task(bind=True)
def opAutoAllocation_task(self, request_data):
        try:
            machines = {m["machine_id"]: m["operation_ids"] for m in request_data["machines"]}
            operations = {
                detail["operation_id"]: {
                    "performing_time": detail["performing_time"],
                    "smv": detail["smv"]
                }
                for detail in request_data["operation_details"]
            }
            employees = {
                op["operator_id"]: op["efficiency"] for op in request_data["operators"]
            }

            problem = LpProblem("Maximize_Bottleneck_Output", LpMaximize)

            x = {
                (m,e): LpVariable(f'machine {m} assigned to employee {e}', cat='Binary')
                for m in machines
                for e in employees
            }

            z = LpVariable("z", lowBound=0, cat="Continuous")

            outputs = {}
            machine_outputs = {}

            for o_id, o_data in operations.items():
                performing_time = o_data['performing_time']
                smv = o_data['smv']

                outputs[o_id] = lpSum(
                    x[m,e] * (performing_time) * employees[e].get(str(o_id),0) / (smv)
                    for m in machines if o_id in machines[m]
                    for e in employees
                )

                for m in machines:    
                    if o_id in machines[m]:
                        machine_outputs[m] = lpSum(
                            x[m,e] * (performing_time) * employees[e].get(str(o_id),0) / (smv)
                            for e in employees
                        )

            #objective function
            problem += z, "Maximize the bottleneck"

            #Constraints

            for o_id, output in outputs.items():
                problem += z <= output
            
            for m in machines:   
                problem += lpSum(x[m,e] for e in employees) == 1

            for e in employees:
                problem += lpSum(x[m,e] for m in machines) <= 1

            problem.solve()

            assignments = {
                f'machine_{m}': f'employee_{e}'
                for m in machines 
                    for e in employees
                    if (x[m,e]).value() >= 0.5
                        if machine_outputs[m].value() > 0
            }   

            hourly_outputs = {}
            for op_id, output in outputs.items():
                hourly_outputs[op_id] = output.value()

            return  request_data, assignments, hourly_outputs, z.value()

        except Exception as e:
            raise self.retry(exc=e)