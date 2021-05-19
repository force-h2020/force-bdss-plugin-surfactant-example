import os
from unittest import TestCase

from traits.testing.api import UnittestTools

from force_gromacs.api import (
    Gromacs_genion, Gromacs_grompp, Gromacs_insert_molecules,
    GromacsTopologyWriter, Gromacs_mdrun, Gromacs_solvate
)

from surfactant_example.ingredient import Ingredient
from surfactant_example.simulation.surfactant_simulation_builder import (
    SurfactantSimulationBuilder
)
from surfactant_example.tests.probe_classes.probe_formulations import (
    ProbeFormulation
)


class TestSurfactantSimulationBuilder(TestCase, UnittestTools):

    def setUp(self):

        name = 'test_experiment'
        size = 4000
        n_steps = 1000
        directory = '.'
        martini_parameters = 'test_martini.itp'
        md_min_parameters = 'test_min_parm.mdp'
        md_prod_parameters = 'test_prod_parm.mdp'

        formulation = ProbeFormulation()

        self.sim_builder = SurfactantSimulationBuilder(
            name=name, size=size, n_steps=n_steps,
            directory=directory,
            martini_parameters=martini_parameters,
            minimize_parameters=md_min_parameters,
            production_parameters=md_prod_parameters,
            formulation=formulation
        )

    def test__init__(self):

        self.assertEqual('test_experiment', self.sim_builder.name)
        self.assertEqual('.', self.sim_builder.directory)
        self.assertEqual(
            'test_martini.itp', self.sim_builder.martini_parameters
        )
        self.assertEqual(
            'test_min_parm.mdp', self.sim_builder.minimize_parameters
        )
        self.assertEqual(
            'test_prod_parm.mdp', self.sim_builder.production_parameters
        )

        self.assertEqual(2, len(self.sim_builder.surfactants))
        self.assertEqual(1, len(self.sim_builder.salts))

        self.assertEqual(71, self.sim_builder.surfactants[0].n_mol)
        self.assertEqual(33, self.sim_builder.surfactants[1].n_mol)
        self.assertEqual(8, self.sim_builder.salts[0].n_mol)
        self.assertEqual(3888, self.sim_builder.solvent.n_mol)

        exp_folder = os.path.join(os.path.curdir, 'test_experiment')
        self.assertEqual(
            os.path.join(exp_folder, '1_init'),
            self.sim_builder.init_folder
        )
        self.assertEqual(
            os.path.join(exp_folder, '2_solvate'),
            self.sim_builder.solvate_folder
        )
        self.assertEqual(
            os.path.join(exp_folder, '3_ions'),
            self.sim_builder.ions_folder
        )
        self.assertEqual(
            os.path.join(exp_folder, '4_minimize'),
            self.sim_builder.minimize_folder
        )
        self.assertEqual(
            os.path.join(exp_folder, '5_production'),
            self.sim_builder.production_folder
        )

    def test__update_n_mols(self):

        self.sim_builder.size = 5000
        self.sim_builder._update_n_mols()

        n_mols = [89, 41, 10, 4860]
        total_n = 0

        for i, ingredient in enumerate(
                self.sim_builder.formulation.ingredients):
            self.assertEqual(n_mols[i], ingredient.n_mol)
            total_n += ingredient.n_mol

        self.assertEqual(self.sim_builder.size, total_n)

    def test__update_cell_dim(self):

        for ingredient, n_mol in zip(
                self.sim_builder.formulation.ingredients,
                [89, 41, 10, 4860]):
            ingredient.n_mol = n_mol

        self.sim_builder._update_cell_dim()

        for dim in self.sim_builder.cell_dim:
            self.assertAlmostEqual(5.5784113, dim)

    def test__update_topology_data(self):

        self.sim_builder._update_topology_data('some_top.itp', 'Mol', 10)
        self.assertEqual(
            ['some_top.itp'], self.sim_builder.topology_data.molecule_files
        )
        self.assertEqual(
            {'Mol': 10}, self.sim_builder.topology_data.fragment_ledger
        )

        self.sim_builder._update_topology_data('some_other_top.itp', 'At', 10)
        self.assertEqual(
            ['some_top.itp',
             'some_other_top.itp'],
            self.sim_builder.topology_data.molecule_files
        )
        self.assertEqual(
            {'Mol': 10,
             'At': 10}, self.sim_builder.topology_data.fragment_ledger
        )

        self.sim_builder._update_topology_data('and_another_top.itp')
        self.assertEqual(
            ['some_top.itp',
             'some_other_top.itp',
             'and_another_top.itp'],
            self.sim_builder.topology_data.molecule_files
        )
        self.assertEqual(
            {'Mol': 10,
             'At': 10}, self.sim_builder.topology_data.fragment_ledger
        )

        self.sim_builder._update_topology_data(symbol='Mol', n_mol=100)
        self.assertEqual(
            ['some_top.itp',
             'some_other_top.itp',
             'and_another_top.itp'],
            self.sim_builder.topology_data.molecule_files
        )
        self.assertEqual(
            {'Mol': 110,
             'At': 10}, self.sim_builder.topology_data.fragment_ledger
        )

    def test_sort_ingredients(self):

        ingredients = self.sim_builder.formulation.ingredients

        surfactants = self.sim_builder.sort_ingredients(
            'Surfactant'
        )

        self.assertEqual(2, len(surfactants))
        self.assertIsInstance(surfactants[0], Ingredient)
        self.assertIsInstance(surfactants[1], Ingredient)

        self.assertListEqual(
            ingredients[:2], surfactants
        )

        self.sim_builder.formulation.concentrations = [
            3, 12, 0.5, 84.5
        ]

        surfactants = self.sim_builder.sort_ingredients(
            'Surfactant'
        )

        self.assertEqual(2, len(surfactants))
        self.assertListEqual(
            ingredients[:2], surfactants[::-1]
        )

        # Test redundancy when both surfactant concentrations
        # are the same
        self.sim_builder.formulation.concentrations = [
            7.5, 7.5, 0.5, 84.5
        ]

        surfactants = self.sim_builder.sort_ingredients(
            'Surfactant'
        )
        self.assertEqual(2, len(surfactants))
        self.assertListEqual(
            ingredients[:2], surfactants
        )

    def test__add_surfactant(self):
        self.sim_builder.cell_dim = [10, 10, 10]
        self.sim_builder._add_surfactant(
            'input_coord', 'surf_coord', 4, 'output_coord',
            'test')
        self.assertEqual(1, len(self.sim_builder._pipeline))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('insert_molecules_test', name)
        self.assertIsInstance(command, Gromacs_insert_molecules)
        flags = list(command.command_options.keys())
        self.assertListEqual(
            ['-f', '-ci', '-nmol', '-o', '-box'], flags
        )
        self.assertEqual(
            'input_coord', command.command_options['-f']
        )
        self.assertEqual(
            'surf_coord', command.command_options['-ci']
        )
        self.assertEqual(
            4, command.command_options['-nmol'],
        )
        self.assertListEqual(
            [10, 10, 10],
            command.command_options['-box'],
        )
        self.assertEqual(
            'output_coord',
            command.command_options['-o']
        )

    def test__add_solvent(self):

        self.sim_builder._add_solvent(
            'input_coord', 'solvent_coord', 4, 'output_coord',
            'test')
        self.assertEqual(1, len(self.sim_builder._pipeline))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('solvate_test', name)
        self.assertIsInstance(command, Gromacs_solvate)
        flags = list(command.command_options.keys())
        self.assertListEqual(
            ['-cp', '-cs', '-maxsol', '-o'], flags
        )
        self.assertEqual(
            'input_coord', command.command_options['-cp']
        )
        self.assertEqual(
            'solvent_coord', command.command_options['-cs']
        )
        self.assertEqual(
            4, command.command_options['-maxsol'],
        )
        self.assertEqual(
            'output_coord',
            command.command_options['-o']
        )

    def test__add_ions(self):

        salt = self.sim_builder.salts[0]

        self.sim_builder._add_ions(
            salt.fragments, salt.n_mol, 'binary_file', 'topology_file',
            'output_coord', 'salt_0'
        )

        self.assertEqual(1, len(self.sim_builder._pipeline))
        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('genion_salt_0', name)
        self.assertIsInstance(command, Gromacs_genion)
        self.assertEqual(
            'binary_file', command.command_options['-s']
        )
        self.assertEqual(
            'topology_file', command.command_options['-p']
        )
        self.assertEqual(
            'output_coord', command.command_options['-o']
        )
        self.assertEqual(
            'PI', command.command_options['-pname']
        )
        self.assertEqual(8, command.command_options['-np'])
        self.assertEqual(1, command.command_options['-pq'])
        self.assertEqual(
            'NI', command.command_options['-nname']
        )
        self.assertEqual(8, command.command_options['-nn'])
        self.assertEqual(-1, command.command_options['-nq'])

    def test__add_mdrun(self):

        self.sim_builder._add_mdrun(
            'binary', 'energy', 'traj', 'coordinate',
            'log', 'state', "comp_traj", 'test'
        )

        self.assertEqual(1, len(self.sim_builder._pipeline))
        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('mdrun_test', name)
        self.assertIsInstance(command, Gromacs_mdrun)
        self.assertEqual(
            'binary', command.command_options['-s']
        )
        self.assertEqual(
            'energy', command.command_options['-e']
        )
        self.assertEqual(
            'traj', command.command_options['-o'],
        )
        self.assertEqual(
            'comp_traj', command.command_options['-x'],
        )
        self.assertEqual(
            'coordinate', command.command_options['-c'],
        )
        self.assertEqual(
            'log', command.command_options['-g'],
        )
        self.assertEqual(
            'state', command.command_options['-cpo'],
        )

    def test__make_binary(self):

        self.sim_builder._make_binary(
            'topology_file', 'input_coord', 'binary_file',
            'md_parameters', 'test'
        )

        self.assertEqual(1, len(self.sim_builder._pipeline))
        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('grompp_test', name)
        self.assertIsInstance(command, Gromacs_grompp)
        self.assertEqual(
            'md_parameters', command.command_options['-f']
        )
        self.assertEqual(
            'topology_file', command.command_options['-p']
        )
        self.assertEqual(
            'input_coord', command.command_options['-c'],
        )
        self.assertEqual(
            'binary_file', command.command_options['-o'],
        )
        self.assertEqual(4, command.command_options['-maxwarn'])

    def test__make_topology(self):

        self.sim_builder._make_topology()

        self.assertEqual(1, len(self.sim_builder._pipeline))
        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('top_file', name)
        self.assertIsInstance(command, GromacsTopologyWriter)

        self.assertEqual('test_experiment', command.sim_name)
        self.assertEqual(
            os.path.join(os.path.curdir, 'test_experiment'),
            command.directory)
        self.assertEqual('test_experiment_topol.top', command.top_name)

    def test__init_simulation(self):
        init_path = os.path.join(
            os.path.curdir, 'test_experiment', '1_init')

        self.sim_builder._init_simulation()
        self.assertEqual(2, len(self.sim_builder._pipeline))
        self.assertEqual(
            2, len(self.sim_builder.topology_data.molecule_files))
        self.assertEqual(
            2, len(self.sim_builder.topology_data.fragment_ledger))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('insert_molecules_surfactant_0', name)
        self.assertEqual(
            'test_surf_1.gro', command.command_options['-f']
        )
        self.assertEqual(
            'test_surf_1.gro', command.command_options['-ci']
        )
        self.assertEqual(
            70, command.command_options['-nmol'],
        )
        self.assertEqual(
            os.path.join(init_path, 'test_experiment_coord.gro'),
            command.command_options['-o'],
        )

        name, command = self.sim_builder._pipeline.steps[1]
        self.assertEqual('insert_molecules_surfactant_1', name)
        self.assertEqual(
            os.path.join(init_path, 'test_experiment_coord.gro'),
            command.command_options['-f']
        )
        self.assertEqual(
            'test_surf_2.gro', command.command_options['-ci']
        )
        self.assertEqual(
            33, command.command_options['-nmol'],
        )
        self.assertEqual(
            os.path.join(init_path, 'test_experiment_coord.gro'),
            command.command_options['-o'],
        )

    def test__solvate_simulation(self):
        exp_path = os.path.join(os.path.curdir, 'test_experiment')

        self.sim_builder._solvate_simulation()
        self.assertEqual(1, len(self.sim_builder._pipeline))
        self.assertEqual(
            1, len(self.sim_builder.topology_data.molecule_files))
        self.assertEqual(
            1, len(self.sim_builder.topology_data.fragment_ledger))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('solvate_solvent_0', name)
        self.assertEqual(
            os.path.join(exp_path, '1_init',
                         'test_experiment_coord.gro'),
            command.command_options['-cp']
        )
        self.assertEqual(
            'test_solvent.gro', command.command_options['-cs']
        )
        self.assertEqual(
            3888, command.command_options['-maxsol'],
        )
        self.assertEqual(
            os.path.join(exp_path, '2_solvate',
                         'test_experiment_coord.gro'),
            command.command_options['-o'],
        )

    def test__ions_simulation(self):

        self.sim_builder._ions_simulation()
        self.assertEqual(6, len(self.sim_builder._pipeline))
        self.assertEqual(
            2, len(self.sim_builder.topology_data.molecule_files))
        self.assertEqual(
            0, len(self.sim_builder.topology_data.fragment_ledger))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('top_file', name)

        name, command = self.sim_builder._pipeline.steps[1]
        self.assertEqual('grompp_ions_0', name)
        self.assertEqual(
            'test_min_parm.mdp', command.command_options['-f']
        )

        name, command = self.sim_builder._pipeline.steps[2]
        self.assertEqual('genion_surfactant_0', name)
        self.assertEqual(
            'PI', command.command_options['-pname']
        )
        self.assertEqual(71, command.command_options['-np'])
        self.assertEqual(1, command.command_options['-pq'])

        name, command = self.sim_builder._pipeline.steps[3]
        self.assertEqual('grompp_surfactant_ions_0', name)
        self.assertEqual(
            'test_min_parm.mdp', command.command_options['-f']
        )

        name, command = self.sim_builder._pipeline.steps[4]
        self.assertEqual('genion_salt_0', name)
        self.assertIsInstance(command, Gromacs_genion)
        self.assertEqual(
            'PI', command.command_options['-pname']
        )
        self.assertEqual(8, command.command_options['-np'])
        self.assertEqual(1, command.command_options['-pq'])
        self.assertEqual(
            'NI', command.command_options['-nname']
        )
        self.assertEqual(8, command.command_options['-nn'])
        self.assertEqual(-1, command.command_options['-nq'])

        name, command = self.sim_builder._pipeline.steps[5]
        self.assertEqual('grompp_salt_ions_0', name)
        self.assertEqual(
            'test_min_parm.mdp', command.command_options['-f']
        )

    def test__minimize_simulation(self):
        exp_path = os.path.join(os.path.curdir, 'test_experiment')
        ions_path = os.path.join(exp_path, '3_ions')
        minimize_path = os.path.join(exp_path, '4_minimize')

        self.sim_builder._minimize_simulation()
        self.assertEqual(1, len(self.sim_builder._pipeline))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('mdrun_minimize', name)
        self.assertEqual(
            self.sim_builder.mpi_run, command.mpi_run
        )
        self.assertEqual(
            os.path.join(ions_path, 'test_experiment_topol.tpr'),
            command.command_options['-s']
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_ener.edr'),
            command.command_options['-e']
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_traj.xtc'),
            command.command_options['-x'],
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_coord.gro'),
            command.command_options['-c'],
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_md.log'),
            command.command_options['-g'],
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_state.cpt'),
            command.command_options['-cpo'],
        )

    def test__production_simulation(self):
        exp_path = os.path.join(os.path.curdir, 'test_experiment')
        minimize_path = os.path.join(exp_path, '4_minimize')
        prod_path = os.path.join(exp_path, '5_production')

        self.sim_builder._production_simulation()
        self.assertEqual(2, len(self.sim_builder._pipeline))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('grompp_production', name)
        self.assertEqual(
            'test_prod_parm.mdp', command.command_options['-f']
        )
        self.assertEqual(
            os.path.join(exp_path, 'test_experiment_topol.top'),
            command.command_options['-p']
        )
        self.assertEqual(
            os.path.join(minimize_path, 'test_experiment_coord.gro'),
            command.command_options['-c'],
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_topol.tpr'),
            command.command_options['-o'],
        )

        name, command = self.sim_builder._pipeline.steps[1]
        self.assertEqual('mdrun_production', name)
        self.assertEqual(
            self.sim_builder.mpi_run, command.mpi_run
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_topol.tpr'),
            command.command_options['-s']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.trr'),
            command.command_options['-o']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_ener.edr'),
            command.command_options['-e']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.xtc'),
            command.command_options['-x'],
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_coord.gro'),
            command.command_options['-c'],
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_md.log'),
            command.command_options['-g'],
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_state.cpt'),
            command.command_options['-cpo'],
        )
        self.assertEqual(
            1000,
            command.command_options['-nsteps'],
        )

    def test___post_process_results(self):
        exp_path = os.path.join(os.path.curdir, 'test_experiment')
        prod_path = os.path.join(exp_path, '5_production')

        self.sim_builder._post_process_results()
        self.assertEqual(3, len(self.sim_builder._pipeline))

        name, command = self.sim_builder._pipeline.steps[0]
        self.assertEqual('g_select', name)
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.xtc'),
            command.command_options['-f']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.ndx'),
            command.command_options['-on']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_topol.tpr'),
            command.command_options['-s']
        )
        self.assertEqual(
            '( resname PS1 ) or ( resname SS )',
            command.user_input,
        )

        name, command = self.sim_builder._pipeline.steps[1]
        self.assertEqual('trjconv_nojump', name)
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.xtc'),
            command.command_options['-f']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_topol.tpr'),
            command.command_options['-s']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.ndx'),
            command.command_options['-n']
        )
        self.assertEqual(
            os.path.join(
                prod_path, 'test_experiment_results_PS1_SS.gro'),
            command.command_options['-o']
        )
        self.assertEqual(
            'nojump',
            command.command_options['-pbc']
        )

        name, command = self.sim_builder._pipeline.steps[2]
        self.assertEqual('trjconv_whole', name)
        self.assertEqual(
            os.path.join(
                prod_path, 'test_experiment_results_PS1_SS.gro'),
            command.command_options['-f']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_topol.tpr'),
            command.command_options['-s']
        )
        self.assertEqual(
            os.path.join(prod_path, 'test_experiment_traj.ndx'),
            command.command_options['-n']
        )
        self.assertEqual(
            os.path.join(
                prod_path, 'test_experiment_results_PS1_SS.gro'),
            command.command_options['-o']
        )
        self.assertEqual(
            'whole',
            command.command_options['-pbc']
        )

    def test_build_pipeline(self):

        pipeline = self.sim_builder.build_pipeline()

        self.assertEqual(16, len(pipeline))

        names, commands = zip(*pipeline.steps)

        self.assertListEqual(
            ['file_tree', 'insert_molecules_surfactant_0',
             'insert_molecules_surfactant_1',
             'solvate_solvent_0', 'top_file', 'grompp_ions_0',
             'genion_surfactant_0', 'grompp_surfactant_ions_0',
             'genion_salt_0', 'grompp_salt_ions_0',
             'mdrun_minimize',
             'grompp_production', 'mdrun_production', 'g_select',
             'trjconv_nojump', 'trjconv_whole'],
            list(names)
        )
