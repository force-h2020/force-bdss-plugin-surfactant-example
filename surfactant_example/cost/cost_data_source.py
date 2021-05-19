from force_bdss.api import BaseDataSource, DataValue, Slot


class CostDataSource(BaseDataSource):
    """Class that calculates cost of fragment materials
    for a production run of a certain Gromacs simulation"""

    def run(self, model, parameters):

        formulation = parameters[0].value

        total_cost = formulation.price

        pass_mark = (total_cost < model.threshold)

        model.notify_pass_mark(pass_mark)

        return [
                DataValue(type="COST", value=total_cost)
            ]

    def slots(self, model):
        return (
            (
                Slot(description=f"Chemical formulation data",
                     type="FORMULATION"),
            ),
            (
                Slot(description="Cost of simulation",
                     type="COST"),
            )
        )
