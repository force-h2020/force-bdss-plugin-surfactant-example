from traits.api import Float

from force_bdss.api import BaseDataSourceModel

from surfactant_example.mco.driver_events import KPIProgressEvent


class CostDataSourceModel(BaseDataSourceModel):
    """Class that calculates viscosity from Gromacs
    simulation results"""

    # Upper threshold for cost of formulation in $USD
    threshold = Float(0.0, desc='Upper cost threshold in $USD')

    def notify_pass_mark(self, pass_mark):
        """Notify whether a simulation has produced an acceptable.
        property value. Assigns an `KPIProgressEvent` to the
        `event` attribute on associated
        `CostDataSourceModel`. By doing so it can be picked
        up by the `SurfactantMCO` and passed onto any
        `NotificationListeners` present.

        Parameters
        ----------
        pass_mark: bool
            A string containing the constructed
            bash script to run a Gromacs experiment.
        """

        if pass_mark:
            value = 'PASS'
        else:
            value = 'FAIL'

        self.notify(
            KPIProgressEvent(
                name='cost_pass',
                value=value
            )
        )
