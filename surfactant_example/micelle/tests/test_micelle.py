from unittest import TestCase

import numpy as np

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue
from force_gromacs.tests.fixtures import gromacs_coordinate_file

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.tests.probe_classes.probe_formulations import (
    ProbeFormulation,
)


class TestMicelleDataSource(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[3]
        self.data_source = self.factory.create_data_source()

        self.traj_file = gromacs_coordinate_file
        self.formulation = ProbeFormulation()

    def test_basic_function(self):

        # Test molecular clustering
        model = self.factory.create_model()
        model.fragment_symbols = ["PS1", "SS"]
        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(2, len(in_slots))
        values = [self.formulation, self.traj_file]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]

        with self.assertTraitChanges(model, "event", count=1):
            res = self.data_source.run(model, data_values)

        self.assertEqual(2, res[0].value)

        # Test atomic clustering
        model.method = "atomic"
        model.atom_thresh = 1

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]

        res = self.data_source.run(model, data_values)

        self.assertEqual(2, res[0].value)

    def test_calculate_aggregation_numbers(self):

        trajectory_data = {
            "mol_ref": ["1PS1", "1PS1", "2SS", "2SS"],
            "coord": np.array(
                [
                    [
                        [0.546, 0.326, 0.070],
                        [0.285, 0.135, 0.310],
                        [0.212, 0.178, 0.770],
                        [0.166, 0.422, 1.173],
                    ],
                    [
                        [0.546, 0.326, 0.070],
                        [0.285, 0.135, 0.310],
                        [0.212, 0.178, 0.770],
                        [0.166, 0.422, 1.173],
                    ],
                ]
            ),
            "dim": np.array(
                [[4.36258, 4.36258, 4.36258], [4.36258, 4.36258, 4.36258]]
            ),
        }

        primary_surfactant = self.formulation.ingredients[0].fragments[0]
        secondary_surfactant = self.formulation.ingredients[1].fragments[0]

        agg_num = self.data_source.calculate_aggregation_numbers(
            trajectory_data, [primary_surfactant]
        )
        self.assertEqual((2,), agg_num.shape)
        self.assertTrue(np.allclose(np.zeros(2), agg_num))

        agg_num = self.data_source.calculate_aggregation_numbers(
            trajectory_data,
            [primary_surfactant, secondary_surfactant],
            cluster_thresh=1,
            noise_thresh=1,
        )
        self.assertEqual((2,), agg_num.shape)
        self.assertTrue(np.allclose(np.array([2, 2]), agg_num))

    def test_notify_pass_mark(self):
        model = self.factory.create_model()
        pass_mark = True

        with self.assertTraitChanges(model, "event", count=1):
            model.notify_pass_mark(pass_mark)
