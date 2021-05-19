import numpy as np

from force_bdss.api import BaseDataSource, DataValue, Slot
from force_gromacs.api import GromacsCoordinateReader, molecular_positions

from .cluster import cluster, label_set
from .utilities import numpy_count


class MicelleDataSource(BaseDataSource):
    """Class that calculates the micelle aggregation number from
     Gromacs surfactant simulation results"""

    # Reader for Gromacs .gro files
    _reader = GromacsCoordinateReader()

    def calculate_aggregation_numbers(
        self,
        trajectory,
        fragments,
        r_thresh=1.25,
        noise_thresh=5,
        cluster_thresh=20,
        method="molecular",
        atom_thresh=5,
    ):
        """Takes in a Gromacs trajectory containing information on a set
        of Fragment objects that can form micelles. Clusters the molecular
        coordinates of all Fragment molecules at each time step and returns
        a moving average of the cluster size throughout the simulation

        Parameters
        ----------
        trajectory: dict
            Data from a Gromacs trajectory file, loaded by a
            GromacsCoordinateReader. Contains molecular coordinate information
            throughout a simulation
        fragments: list of Fragment
            List of Fragment objects representing surfactants expected to have
            formed micelles during the simulation
        r_thresh: float, optional
            Upper threshold in nanometers for radial distance to consider
            whether two molecules are neighbours
        noise_thresh: int, optional
            Lower threshold on number of neighbouring molecules to be
            considered part of a cluster
        cluster_thresh: int, optional
            Lower threshold on cluster size
        """

        # Obtain key trajectory information
        n_frames = trajectory["coord"].shape[0]
        dimensions = trajectory["dim"]
        fragment_indices = [
            self._reader.extract_molecules(trajectory, fragment.symbol)
            for fragment in fragments
        ]
        mol_ref = np.asarray(trajectory["mol_ref"])
        mol_ref = mol_ref[np.concatenate(fragment_indices)]

        # Initialise micelle aggregation numbers
        cluster_sizes = []
        mean_aggregation_numbers = np.zeros(n_frames)

        # Cycle through each frame in the trajectory
        for frame in range(n_frames):

            # Collate all molecular fragments to be included in clusters
            # for this frame
            molecules = np.empty((0, 3), dtype=float)

            if method == "molecular":
                # Cycle through each fragment
                for indices, fragment in zip(fragment_indices, fragments):

                    # Find coordinates in trajectory relating to fragment
                    coordinates = trajectory["coord"][frame, indices]
                    n_site = len(fragment.atoms)
                    masses = fragment.get_masses()

                    # Return a single set of molecular coordinates for fragment
                    fragment_mol = molecular_positions(
                        coordinates,
                        n_site,
                        masses,
                        mode="sites",
                        com_sites=[0],
                    )

                    # Append to clustering array
                    molecules = np.concatenate((molecules, fragment_mol))
            else:
                molecules = trajectory["coord"][
                    frame, np.concatenate(fragment_indices)
                ]

            # Assign labels to each molecule based on clustering analysis
            cluster_labels = cluster(
                molecules,
                dimensions[frame],
                r_thresh=r_thresh,
                noise_thresh=noise_thresh,
                cluster_thresh=cluster_thresh,
                method=method,
                mol_ref=mol_ref,
                atom_thresh=atom_thresh,
            )

            # Append cluster sizes to list
            cluster_sizes += [
                numpy_count(cluster_labels, label)
                for label in label_set(cluster_labels)
            ]

            # Calculate the moving average for each frame
            if len(cluster_sizes) > 0:
                mean_aggregation_numbers[frame] = np.mean(cluster_sizes)

        return mean_aggregation_numbers

    def run(self, model, parameters):

        formulation = parameters[0].value
        trajectory_file = parameters[1].value

        # Read trajectory file to return simulation data of fragments
        trajectory_data = self._reader.read(
            trajectory_file, symbols=model.fragment_symbols
        )

        # Obtain Fragment objects that correspond to the required symbols
        fragments = formulation.fragment_search(model.fragment_symbols)

        # Calculate moving average of micelle aggregation numbers for each
        # frame of trajectory
        aggregation_numbers = self.calculate_aggregation_numbers(
            trajectory_data,
            fragments,
            r_thresh=model.r_thresh,
            noise_thresh=model.noise_thresh,
            cluster_thresh=model.cluster_thresh,
        )

        pass_mark = aggregation_numbers[-1] > model.threshold

        model.notify_pass_mark(pass_mark)

        return [DataValue(type="AGGREGATION", value=aggregation_numbers[-1])]

    def slots(self, model):

        return (
            (
                Slot(
                    description="Chemical formulation data", type="FORMULATION"
                ),
                Slot(
                    description="Simulation trajectory file", type="TRAJECTORY"
                ),
            ),
            (
                Slot(
                    description="Calculated micelle aggregation number"
                    " of surfactant",
                    type="AGGREGATION",
                ),
            ),
        )
