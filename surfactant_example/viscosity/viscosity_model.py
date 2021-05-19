from traits.api import Float

from force_bdss.api import BaseDataSourceModel

from surfactant_example.mco.driver_events import KPIProgressEvent


class ViscosityDataSourceModel(BaseDataSourceModel):
    """Class that calculates viscosity from Gromacs
    simulation results"""

    threshold = Float(0.0)

    def notify_pass_mark(self, pass_mark):
        """Notify whether a simulation has produced an acceptable.
        property value. Assigns an `KPIProgressEvent` to the
        `event` attribute. By doing so it can be picked
        up by the `Workflow` and passed onto any
        `NotificationListeners` present.

        Parameters
        ----------
        pass_mark: bool
            Pass mark for viscosity KPI
        """
        value = "PASS" if pass_mark else "FAIL"

        self.notify(KPIProgressEvent(name="viscosity_pass", value=value))
