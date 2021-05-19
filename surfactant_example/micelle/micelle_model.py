from traits.api import Float, Int, Enum, List, Unicode
from traitsui.api import View, Item

from force_bdss.api import BaseDataSourceModel

from surfactant_example.mco.driver_events import KPIProgressEvent


class MicelleDataSourceModel(BaseDataSourceModel):
    """Class that calculates micelle aggregation nummber from
     Gromacs surfactant simulation results"""

    # Symbols of different surfactant fragments contained in
    # micelle simulations
    fragment_symbols = List(
        Unicode,
        desc='List of sumbols corresponding to surfactant fragments')

    # Upper threshold on clustering radial distance
    r_thresh = Float(
        1.25, desc='Upper threshold on clustering radial distance'
    )

    # Lower threshold on number of neighbours for clustering
    noise_thresh = Int(
        1, desc='Lower threshold on number of neighbours for clustering'
    )

    # Lower threshold on cluster size
    cluster_thresh = Int(2, desc='Lower threshold on cluster size')

    # Clustering method
    method = Enum('molecular', 'atomic', desc='Clustering method')

    # Threshold number of atomic neighbours for a molecular neighbour
    atom_thresh = Int(
        5, desc='Lower threshold number of atomic neighbours for '
                'a molecular neighbour'
    )

    # Lower threshold on accepted aggregation number
    threshold = Float(0.0)

    traits_view = View(
        Item('fragment_symbols'),
        Item('method'),
        Item('r_thresh'),
        Item('noise_thresh'),
        Item('cluster_thresh'),
        Item('atom_thresh', visible_when="method=='atomic'"),
        Item('threshold'),
    )

    def notify_pass_mark(self, pass_mark):
        """Notify whether a simulation has produced an acceptable.
        property value. Assigns an `KPIProgressEvent` to the
        `event` attribute. By doing so it can be picked
        up by the `Workflow` and passed onto any
        `NotificationListeners` present.

        Parameters
        ----------
        pass_mark: bool
            Pass mark for micelle KPI
        """
        value = "PASS" if pass_mark else "FAIL"
        self.notify(
            KPIProgressEvent(
                name="micelle_pass",
                value=value
            )
        )
