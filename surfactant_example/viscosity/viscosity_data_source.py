import numpy as np

from force_bdss.api import BaseDataSource, DataValue, Slot


class ViscosityDataSource(BaseDataSource):
    """Class that calculates viscosity from Gromacs
    simulation results"""

    def run(self, model, parameters):

        values = [p.value for p in parameters]

        viscosity = np.exp(-0.5 * (values[0] - 1) ** 2 / (2 * np.pi))

        pass_mark = viscosity > model.threshold

        model.notify_pass_mark(pass_mark)

        return [DataValue(type="VISCOSITY", value=viscosity)]

    def slots(self, model):

        return (
            (Slot(description="Simulation results", type="RESULTS"),),
            (
                Slot(
                    description="Calculated viscosity of surfactant",
                    type="VISCOSITY",
                ),
            ),
        )
