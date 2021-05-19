import numpy as np

from force_bdss.api import Slot, BaseDataSource, DataValue


SQRT2PI = np.sqrt(2 * np.pi)


def gaussian(x, mean, sigma):
    """Returns the value of a Gaussian function at x, with mean
    and sigma parameters"""
    return np.exp(- 0.5 * ((mean - x) / sigma) ** 2) / (sigma * SQRT2PI)


class TrialViscosityDataSource(BaseDataSource):
    """Calculates formulation viscosity from a simple toy model
    using Formulation ingredients"""

    def formulation_viscosity(self, model, formulation):
        """Calculates viscosity of formulation from contributions of
        ingredients present. The total viscosity is obtained by either
        the sum or product of each contribution"""
        names = [ingredient.name for ingredient in formulation.ingredients]
        means = []
        sigmas = []
        concentrations = []

        for parameters in model.ingredient_models:
            if parameters.name in names:

                sigmas.append(parameters.sigma)
                means.append(parameters.mean)

                index = names.index(parameters.name)
                concentrations.append(formulation.concentrations[index])

        # Generate viscosity contributions from simple Gaussian model
        viscosities = gaussian(
            np.asarray(concentrations),
            np.asarray(means),
            np.asarray(sigmas)
        )

        if model.calculation_mode == 'Sum':
            return viscosities.sum()
        return viscosities.prod()

    def run(self, model, parameters):

        formulation = parameters[0].value

        viscosity = self.formulation_viscosity(
            model, formulation)

        return [
            DataValue(type="VISCOSITY", value=viscosity)
        ]

    def slots(self, model):

        input_slots = (
            Slot(
                description=f"Chemical formulation data",
                type="FORMULATION"),
        )

        output_slots = (
            Slot(
                description=f"Formulation viscosity",
                type="VISCOSITY"),
        )

        return (
            input_slots,
            output_slots
        )
