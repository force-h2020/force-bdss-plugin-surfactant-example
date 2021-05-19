import os
from operator import itemgetter

from scipy.constants import N_A

from traits.api import (
    List, Unicode, Property, Instance
)

from force_gromacs.api import (
    Gromacs_solvate, Gromacs_insert_molecules, Gromacs_grompp, Gromacs_genion,
    Gromacs_mdrun, Gromacs_select, Gromacs_trjconv,
    BaseGromacsSimulationBuilder, GromacsTopologyWriter,
    FileTreeBuilder
)

from surfactant_example.ingredient import Ingredient

from .simulation_utilities import (
    calculate_n_mols
)
from surfactant_example.formulation.formulation import Formulation


class SurfactantSimulationBuilder(BaseGromacsSimulationBuilder):

    # --------------------
    #  Required Attributes
    # --------------------

    #: List of all Ingredient objects
    formulation = Instance(Formulation)

    #: File path for Gromacs energy minimization parameters
    minimize_parameters = Unicode()

    #: File path for Gromacs prodcution run parameters
    production_parameters = Unicode()

    # --------------------
    #  Regular Attributes
    # --------------------

    #: Folder for data regarding initialisation of simulation
    init_folder = Unicode()

    #: Folder for data regarding solvation of simulation
    solvate_folder = Unicode()

    #: Folder for data regarding add ions to simulation
    ions_folder = Unicode()

    #: Folder for data regarding energy minimisation
    #: simulation
    minimize_folder = Unicode()

    #: Folder for data regarding simulation production run
    production_folder = Unicode()

    # Results file name containing surfactant trajectory coordinates for
    # further postprocessing
    results_file = Unicode()

    # --------------------
    #     Properties
    # --------------------

    #: List of surfactant ingredients
    surfactants = Property(
        List(Ingredient),
        depends_on='formulation.[concentrations,ingredients.role]')

    #: List of salt ingredients
    salts = Property(
        List(Ingredient),
        depends_on='formulation.[concentrations,ingredients.role]')

    #: Solvent ingredient
    solvent = Property(
        Instance(Ingredient),
        depends_on='formulation.[concentrations,ingredients.role]')

    def __init__(self, *args, **kwargs):
        super(SurfactantSimulationBuilder, self).__init__(
            *args, **kwargs
        )
        # Initialise ingredient concentrations and number of
        # molecules to add to simulation
        self._update_n_mols()

    # --------------------
    #      Defaults
    # --------------------

    def _init_folder_default(self):
        return os.path.join(self.folder, '1_init')

    def _solvate_folder_default(self):
        return os.path.join(self.folder, '2_solvate')

    def _ions_folder_default(self):
        return os.path.join(self.folder, '3_ions')

    def _minimize_folder_default(self):
        return os.path.join(self.folder, '4_minimize')

    def _production_folder_default(self):
        return os.path.join(self.folder, '5_production')

    def _results_file_default(self):
        return self.name + '_results'

    # --------------------
    #      Listeners
    # --------------------

    def _get_surfactants(self):
        return self.sort_ingredients('Surfactant')

    def _get_salts(self):
        return self.sort_ingredients('Salt')

    def _get_solvent(self):
        return self.sort_ingredients('Solvent')[0]

    # --------------------
    #    Private Methods
    # --------------------

    def _update_n_mols(self):
        """Calculates number of fragments required in simulation
        for each solvent, salt and surfactant and updates their
        respective ingredient objects n_mol attribute"""

        n_mols = calculate_n_mols(
            self.size,
            self.formulation.num_fractions
        )

        n_ion = 0
        for n_mol, ingredient in zip(n_mols, self.formulation.ingredients):
            ingredient.n_mol = n_mol

            # Track the number of ions that will replace solvent
            # molecules
            if ingredient.role == 'Surfactant':
                n_ion += n_mol * (len(ingredient.fragments) - 1)
            elif ingredient.role == 'Salt':
                n_ion += n_mol * len(ingredient.fragments)

        # Check that total solvent molecule count is greater than the
        # number of ions required (these solvent fragments will be replaced
        # by ions in the pre-processing)
        assert self.solvent.n_mol > n_ion, (
            'Invalid number of solvent fragments '
            f'{self.solvent.name}: {self.solvent.n_mol}'
            f' < {n_ion}. '
            'Check input concentrations of ingredients')

    def _update_cell_dim(self, density=1.0):
        """Calculates the size of the simulation cell in nm based
        on an estimation of the formulation density in g cm-3
        """

        # Calculate masses of each ingredient in g
        masses = [
            ingredient.n_mol * ingredient.mass / N_A
            for ingredient in self.formulation.ingredients
        ]

        # Calculate cell volume in nm3
        cell_volume = 1E21 * sum(masses) / density

        # Calculate each dimension in nm, assuming a square cell geometry
        self.cell_dim = [cell_volume ** (1/3) for _ in range(3)]

    def _update_topology_data(self, topology=None, symbol=None, n_mol=0):
        """Updates attribute _topology_data, which stores data to write
        to a human readable Gromacs topology file"""

        if topology is not None:
            self.topology_data.add_molecule_file(topology)

        if symbol is not None:
            self.topology_data.add_fragment(symbol)
            self.topology_data.edit_fragment_number(symbol, n_mol)

    def _add_surfactant(self, input_coordinate, surfactant_coord,
                        n_mol, output_coordinate, tag):
        """Add surfactant molecule to simulation cell"""
        self._pipeline.append(
            (
                f'insert_molecules_{tag}',
                Gromacs_insert_molecules(
                    command_options={
                        '-f': input_coordinate,
                        '-ci': surfactant_coord,
                        '-nmol': n_mol,
                        '-o': output_coordinate,
                        '-box': self.cell_dim},
                )
            )
        )

    def _add_solvent(self, input_coordinate, solvent_coord,
                     n_mol, output_coordinate, tag):
        """Add solvent molecule to simulation cell"""
        self._pipeline.append(
            (
                f'solvate_{tag}',
                Gromacs_solvate(
                    command_options={
                        '-cp': input_coordinate,
                        '-cs': solvent_coord,
                        '-maxsol': n_mol,
                        '-o': output_coordinate
                    }
                )
            )
        )

    def _add_ions(self, ions, n_mol, input_binary, input_topology,
                  output_coordinate, tag):
        """Add atomic ions to simulation cell"""
        command_options = {
            '-s': input_binary,
            '-p': input_topology,
            '-o': output_coordinate
        }

        for ion in ions:
            if ion.charge > 0:
                command_options["-pname"] = ion.symbol
                command_options["-np"] = n_mol
                command_options["-pq"] = int(ion.charge)
            else:
                command_options["-nname"] = ion.symbol
                command_options["-nn"] = n_mol
                command_options["-nq"] = int(ion.charge)

        self._pipeline.append(
            (
                f'genion_{tag}',
                Gromacs_genion(
                    command_options=command_options,
                    user_input='W'
                )
            )
        )

    def _add_mdrun(self, input_binary, output_energy, output_traj,
                   output_coordinate, output_log, output_state,
                   output_comp_traj, tag, n_steps=-2):
        """Add MD simulation run to pipeline"""
        self._pipeline.append(
            (
                f'mdrun_{tag}',
                Gromacs_mdrun(
                    command_options={
                        '-s': input_binary,
                        '-o': output_traj,
                        '-e': output_energy,
                        '-c': output_coordinate,
                        '-g': output_log,
                        '-cpo': output_state,
                        '-x': output_comp_traj,
                        '-nsteps': n_steps
                    },
                    mpi_run=self.mpi_run
                )
            )
        )

    def _add_trjconv(self, input_traj, input_topology, output_coord,
                     index_file):
        """Prepares trajectory for clustering analysis, similar to
        http://www.gromacs.org/Documentation/How-tos/Micelle_Clustering"""

        selection = [f'( resname {surfactant.fragments[0].symbol} )'
                     for surfactant in self.surfactants]
        selection = ' or '.join(selection)

        self._pipeline.append(
            (
                f'g_select',
                Gromacs_select(
                    command_options={
                        '-f': input_traj,
                        '-s': input_topology,
                        '-on': index_file
                    },
                    user_input=selection
                )
            )
        )

        self._pipeline.append(
            (
                f'trjconv_nojump',
                Gromacs_trjconv(
                    command_options={
                        '-f': input_traj,
                        '-s': input_topology,
                        '-o': output_coord,
                        '-pbc': 'nojump',
                        '-n': index_file
                    }
                )
            )
        )

        self._pipeline.append(
            (
                f'trjconv_whole',
                Gromacs_trjconv(
                    command_options={
                        '-f': output_coord,
                        '-s': input_topology,
                        '-o': output_coord,
                        '-pbc': 'whole',
                        '-n': index_file
                    }
                )
            )
        )

    def _make_binary(self, input_topology, input_coordinate,
                     output_binary, md_parameters, tag):
        """Add generation of binary topology file to pipeline"""

        output_topology = os.path.splitext(input_topology)[0] + '.mdp'
        self._pipeline.append(
            (
                f'grompp_{tag}',
                Gromacs_grompp(
                    command_options={
                        '-f': md_parameters,
                        '-p': input_topology,
                        '-c': input_coordinate,
                        '-o': output_binary,
                        '-maxwarn': 4,
                        '-po': output_topology
                    }
                )
            )
        )

    def _make_topology(self):
        """Add generation of human readable topology file to pipeline"""
        self._pipeline.append(
            (
                'top_file',
                GromacsTopologyWriter(
                    topology_data=self.topology_data,
                    sim_name=self.name,
                    directory=self.folder,
                    top_name=self.file_registry.top_file
                )
            )
        )

    def _file_tree_builder(self):
        """Add generation of file tree simulation files to be stored
        in to pipeline"""

        self._pipeline.append(
            (
                'file_tree',
                FileTreeBuilder(
                    directory=self.folder,
                    folders=['1_init', '2_solvate',
                             '3_ions', '4_minimize',
                             '5_production'],
                )
            )
        )

    def _init_simulation(self):
        """Write scripts / commands to initialise the simulation
        with surfactant molecules"""

        # Initialise coordinate file with Primary Surfactant
        surfactant = self.surfactants[0]
        input_coordinate = surfactant.fragments[0].coordinate
        output_coordinate = os.path.join(
            self.init_folder, self.file_registry.coord_file)

        self._add_surfactant(
            input_coordinate, input_coordinate,
            surfactant.n_mol-1, output_coordinate,
            'surfactant_0')

        self._update_topology_data(
            surfactant.fragments[0].topology,
            surfactant.fragments[0].symbol,
            surfactant.n_mol
        )

        # Add Secondary Surfactants (optional) to coordinate file
        input_coordinate = output_coordinate
        for i, surfactant in enumerate(self.surfactants[1:]):
            self._add_surfactant(
                input_coordinate, surfactant.fragments[0].coordinate,
                surfactant.n_mol, output_coordinate,
                f'surfactant_{i + 1}')

            self._update_topology_data(
                surfactant.fragments[0].topology,
                surfactant.fragments[0].symbol,
                surfactant.n_mol
            )

    def _solvate_simulation(self):

        # Solvate simulation
        input_coordinate = os.path.join(
            self.init_folder, self.file_registry.coord_file)
        output_coordinate = os.path.join(
            self.solvate_folder, self.file_registry.coord_file)

        for i, fragment in enumerate(self.solvent.fragments):
            self._add_solvent(
                input_coordinate, fragment.coordinate,
                self.solvent.n_mol, output_coordinate, f'solvent_{i}')

            self._update_topology_data(
                fragment.topology,
                fragment.symbol,
                self.solvent.n_mol
            )

    def _ions_simulation(self):

        top_file = self.file_registry.top_file
        coord_file = self.file_registry.coord_file
        binary_file = self.file_registry.binary_file

        input_topology = os.path.join(self.folder, top_file)
        input_coordinate = os.path.join(self.solvate_folder, coord_file)
        output_coordinate = os.path.join(self.ions_folder, coord_file)
        input_binary = os.path.join(self.ions_folder, binary_file)
        output_binary = input_binary

        # Add all the salt ion topologies to the main Gromacs
        # topology file
        for salt in self.salts:
            for ion in salt.fragments:
                self._update_topology_data(ion.topology)

        # Create human readable topology file with fragment ingredient
        # that have been inserted into simulation box
        self._make_topology()

        # Add binary file step to pipeline. This will be used to insert
        # ions using Gromacs genion command
        self._make_binary(input_topology, input_coordinate,
                          output_binary, self.minimize_parameters,
                          'ions_0')

        # Replace some Solvent species with surfactant counter-ion
        for i, surfactant in enumerate(self.surfactants):
            if len(surfactant.fragments) > 1:
                self._add_ions(
                    surfactant.fragments[1:], surfactant.n_mol,
                    input_binary, input_topology, output_coordinate,
                    f'surfactant_{i}')

                # Update binary topology file
                self._make_binary(input_topology, output_coordinate,
                                  output_binary, self.minimize_parameters,
                                  f'surfactant_ions_{i}')

        # Replace some Solvent species with salt ions
        for i, salt in enumerate(self.salts):
            self._add_ions(
                salt.fragments, salt.n_mol,
                input_binary, input_topology, output_coordinate,
                f'salt_{i}')

            # Update binary topology file
            self._make_binary(input_topology, output_coordinate,
                              output_binary, self.minimize_parameters,
                              f'salt_ions_{i}')

    def _minimize_simulation(self):

        coord_file = self.file_registry.coord_file
        binary_file = self.file_registry.binary_file
        energy_file = self.file_registry.energy_file
        log_file = self.file_registry.log_file
        traj_file = self.file_registry.traj_file
        comp_traj_file = self.file_registry.comp_traj_file
        state_file = self.file_registry.state_file

        output_coordinate = os.path.join(self.minimize_folder, coord_file)
        input_binary = os.path.join(self.ions_folder, binary_file)
        output_energy = os.path.join(self.minimize_folder, energy_file)
        output_log = os.path.join(self.minimize_folder, log_file)
        output_traj = os.path.join(self.minimize_folder, traj_file)
        output_comp_traj = os.path.join(self.minimize_folder, comp_traj_file)
        output_state = os.path.join(self.minimize_folder, state_file)

        # Run an energy minimization
        self._add_mdrun(input_binary, output_energy, output_traj,
                        output_coordinate, output_log, output_state,
                        output_comp_traj, 'minimize')

    def _production_simulation(self):

        top_file = self.file_registry.top_file
        coord_file = self.file_registry.coord_file
        binary_file = self.file_registry.binary_file
        energy_file = self.file_registry.energy_file
        log_file = self.file_registry.log_file
        traj_file = self.file_registry.traj_file
        comp_traj_file = self.file_registry.comp_traj_file
        state_file = self.file_registry.state_file

        input_topology = os.path.join(self.folder, top_file)
        input_coordinate = os.path.join(self.minimize_folder, coord_file)
        output_coordinate = os.path.join(self.production_folder, coord_file)
        input_binary = os.path.join(self.production_folder, binary_file)
        output_binary = input_binary
        output_energy = os.path.join(self.production_folder, energy_file)
        output_log = os.path.join(self.production_folder, log_file)
        output_traj = os.path.join(self.production_folder, traj_file)
        output_comp_traj = os.path.join(self.production_folder, comp_traj_file)
        output_state = os.path.join(self.production_folder, state_file)

        # Update binary topology file
        self._make_binary(input_topology, input_coordinate,
                          output_binary, self.production_parameters,
                          'production')

        # Run an MD production run
        self._add_mdrun(input_binary, output_energy, output_traj,
                        output_coordinate, output_log, output_state,
                        output_comp_traj, 'production',
                        n_steps=self.n_steps)

    def _post_process_results(self):

        binary_file = self.file_registry.binary_file
        traj_file = self.file_registry.comp_traj_file

        input_topology = os.path.join(self.production_folder, binary_file)
        input_traj = os.path.join(self.production_folder, traj_file)

        # Perform postprocessing on binary trajectory to obtain human
        # readable file ready for further analysis
        index_file_name = self.file_registry.format_file_name(
            self.file_registry.traj_file, 'index')
        index_file = os.path.join(self.production_folder, index_file_name)

        output_file_path = self.get_results_path()

        self._add_trjconv(input_traj, input_topology, output_file_path,
                          index_file)

    # --------------------
    #    Public Methods
    # --------------------

    def sort_ingredients(self, key):
        """Function that extracts indices of roles that match
        the term key and returns a list of these ordered by their
        corresponding ingredient

        Parameters
        ----------
        key: str
            Key to match to Ingredient role

        Returns
        -------
        ordered_ingredients: list of Ingredient
            List of Ingredient objects where role==key ordered by
            concentration values (high to low)
        """

        # Extract fragments whose role == key, and group with their
        # ingredient parameters
        key_ingredients = self.formulation.ingredient_search([key])
        key_concentrations = [
            self.formulation.concentrations[
                self.formulation.ingredients.index(ingredient)]
            for ingredient in key_ingredients
        ]

        # Return an ordered version of ingredients, sorted by
        # concentrations (high to low)
        ordered_ingredients = [
            ingredient for _, ingredient in sorted(
                zip(key_concentrations, key_ingredients),
                key=itemgetter(0),
                reverse=True
            )
        ]

        return ordered_ingredients

    def build_pipeline(self):

        # Recalculate ingredient concentration attributes
        self._update_n_mols()

        # Recalculate simulation cell dimensions
        self._update_cell_dim()

        # Reset pipeline and topology_data attributes
        delattr(self, '_pipeline')
        delattr(self, 'topology_data')
        self._update_topology_data(self.martini_parameters)

        # Add initial command to build a file tree for this simulation
        # data to be stored in
        self._file_tree_builder()

        # Initialise simulation cell with surfactant molecules
        self._init_simulation()

        # Solvate simulation cell with solvent molecules
        self._solvate_simulation()

        # Add ions to cell by swapping with solvent molecules
        self._ions_simulation()

        # Run energy minimization to reach acceptable starting
        # coordinates
        self._minimize_simulation()

        # Perform a production run simulation to calculate properties
        # from
        self._production_simulation()

        # Call Gromacs post processing utilities to prepare trajectory
        # file for clustering
        self._post_process_results()

        return self._pipeline

    def get_results_path(self):
        """Obtain the results trajectory file path for further
        post-processing"""

        file_path = f'{self.production_folder}/{self.results_file}'
        for surfactant in self.surfactants:
            file_path += f'_{surfactant.fragments[0].symbol}'
        file_path += '.gro'

        return file_path
