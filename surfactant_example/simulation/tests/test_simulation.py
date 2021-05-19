from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.formulation.formulation import Formulation
from surfactant_example.tests.probe_classes.probe_ingredients import (
    ProbePrimaryIngredient,
    ProbeSecondaryIngredient,
    ProbeSaltIngredient,
    ProbeSolventIngredient,
)


class TestSimulationDataSource(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[1]
        self.data_source = self.factory.create_data_source()

        #: Example input values
        self.size = 4000
        self.name = "test_experiment"
        self.martini_parameters = "test_martini.itp"
        self.md_min_parameters = "test_min_parm.mdp"
        self.md_prod_parameters = "test_prod_parm.mdp"

        self.model = self.factory.create_model()
        self.model.n_molecule_types = 4
        self.model.martini_parameters = self.martini_parameters
        self.model.md_prod_parameters = self.md_prod_parameters
        self.model.md_min_parameters = self.md_min_parameters
        self.model.size = self.size
        self.model.name = self.name

        self.surfactants = [
            ProbePrimaryIngredient(),
            ProbeSecondaryIngredient(),
        ]
        self.salt = ProbeSaltIngredient()
        self.solvent = ProbeSolventIngredient()

        self.ingredients = self.surfactants + [self.salt] + [self.solvent]
        self.concentrations = [12, 4, 0.5, 83.5]
        self.formulation = Formulation(
            ingredients=self.ingredients, concentrations=self.concentrations
        )
        self.input_values = [self.formulation]

        self.masses = [
            self.surfactants[0].mass,
            self.surfactants[1].mass,
            self.salt.mass,
            self.solvent.mass,
        ]

    def test_basic_function(self):

        in_slots = self.data_source.slots(self.model)[0]
        self.assertEqual(1, len(in_slots))

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, self.input_values)
        ]

        res = self.data_source.run(self.model, data_values)
        self.assertEqual(1, len(res))

    def test_create_simulation_builder(self):
        in_slots = self.data_source.slots(self.model)[0]

        self.assertEqual(1, len(in_slots))

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, self.input_values)
        ]

        sim_builder = self.data_source.create_simulation_builder(
            self.model, data_values
        )

        self.assertEqual(
            "test_experiment_ps1-pi-12.0-ss-4.0-pi-ni-0.5", sim_builder.name
        )
        self.assertEqual(71, self.surfactants[0].n_mol)
        self.assertEqual(33, self.surfactants[1].n_mol)
        self.assertEqual(8, self.salt.n_mol)
        self.assertEqual(3888, self.solvent.n_mol)
