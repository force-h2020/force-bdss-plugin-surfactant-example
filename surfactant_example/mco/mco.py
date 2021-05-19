import logging
from itertools import product

from force_bdss.api import BaseMCO, DataValue


log = logging.getLogger(__name__)


class MCO(BaseMCO):
    def run(self, evaluator):

        parameters = evaluator.mco_model.parameters

        log.info("Doing MCO run")

        for input_parameters in parameter_grid_generator(parameters):

            kpis = evaluator.evaluate(input_parameters)

            optimal_kpis = [DataValue(value=v) for v in kpis]
            # NOTE: This is a workaround for displaying data from different
            # ingredients in WfManager. Ultimately we should include
            # a DataView object that can handle unicode variables
            optimal_points = [
                DataValue(value=v)
                for v in input_parameters
            ]

            evaluator.mco_model.notify_progress_event(
                optimal_points, optimal_kpis
            )


def parameter_grid_generator(parameters):
    """Function to calculate the number of Gromacs experiments
    required and the combinations of each fragment concentrations"""

    ranges = [parameter.sample_values for parameter in parameters]

    for combo in product(*ranges):
        yield combo


def get_labels(parameters):
    """Generates numerical labels for each categorical
    MCOParameter"""

    label_dict = {}
    label = 1

    for parameter in parameters:
        if hasattr(parameter, "categories"):
            for name in parameter.categories:
                if name not in label_dict:
                    label_dict[name] = label
                    label += 1

    return label_dict
