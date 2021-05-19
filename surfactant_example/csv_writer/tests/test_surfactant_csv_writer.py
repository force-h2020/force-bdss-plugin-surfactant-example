from unittest import TestCase, mock

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue, MCOProgressEvent

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.mco.driver_events import KPIProgressEvent
from surfactant_example.tests.probe_classes.probe_ingredients import (
    ProbePrimaryIngredient,
    ProbeSaltIngredient,
    ProbeSolventIngredient,
)
from surfactant_example.csv_writer.surfactant_csv_writer import (
    SurfactantCSVWriter,
    SurfactantCSVWriterModel,
    SurfactantCSVWriterFactory,
)
from surfactant_example.mco.driver_events import SurfactantMCOStartEvent


_CSVWRITER_OPEN = "force_bdss.notification_listeners.base_csv_writer.open"


class TestCSVWriter(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.notification_listener_factories[0]
        self.notification_listener = self.factory.create_listener()
        self.model = self.factory.create_model()

        self.notification_listener.initialize(self.model)

        self.surfactant = ProbePrimaryIngredient()
        self.salt = ProbeSaltIngredient()
        self.solvent = ProbeSolventIngredient()

        self.surfactant.name = "Primary Surfactant"
        self.salt.name = "Sodium Chloride"
        self.solvent.name = "Water"

        self.parameters = [
            DataValue(name="surfactant_name", value="best chemical ever"),
            DataValue(name="surfactant_conc", value=1.0),
            DataValue(name="salt_conc", value=5.0),
        ]
        self.kpis = [
            DataValue(name="viscosity", value=5.7),
            DataValue(name="cost", value=10),
        ]

    def test_factory(self):
        self.assertEqual(
            "surfactant_csv_writer", self.factory.get_identifier())
        self.assertEqual("Surfactant CSV Writer", self.factory.get_name())
        self.assertIs(self.factory.listener_class, SurfactantCSVWriter)
        self.assertIs(self.factory.model_class, SurfactantCSVWriterModel)
        self.assertIsInstance(self.factory, SurfactantCSVWriterFactory)

    def test_parse_progress_event(self):
        event = MCOProgressEvent(
            optimal_point=self.parameters, optimal_kpis=self.kpis
        )
        self.assertListEqual(
            ["best chemical ever", 1.0, 5.0, 5.7, 10],
            self.notification_listener.parse_progress_event(event),
        )

    def test_parse_start_event(self):
        event = SurfactantMCOStartEvent(
            parameter_names=[p.name for p in self.parameters],
            kpi_names=[k.name for k in self.kpis],
        )
        self.assertListEqual(
            [
                "surfactant_name",
                "surfactant_conc",
                "salt_conc",
                "viscosity",
                "cost",
                "viscosity_pass",
                "cost_pass",
            ],
            self.notification_listener.parse_start_event(event),
        )

        mock_open = mock.mock_open()

        with mock.patch(_CSVWRITER_OPEN, mock_open, create=True):
            self.notification_listener.deliver(event)

            mock_open.assert_called_once()

        mock_open.reset_mock()

        self.assertDictEqual(
            self.notification_listener.row_data,
            dict.fromkeys(self.notification_listener.parse_start_event(event)),
        )

    def test_parse_kpi_progress_event(self):
        event = KPIProgressEvent(name="viscosity_pass", value="PASS")
        self.assertDictEqual(
            {}, self.notification_listener.parse_kpiprogress_event(event)
        )

        start_event = SurfactantMCOStartEvent(
            parameter_names=[p.name for p in self.parameters],
            kpi_names=[k.name for k in self.kpis],
        )
        mock_open = mock.mock_open()
        with mock.patch(_CSVWRITER_OPEN, mock_open, create=True):
            self.notification_listener.deliver(start_event)
        mock_open.reset_mock()
        self.assertDictEqual(
            {"viscosity_pass": "PASS"},
            self.notification_listener.parse_kpiprogress_event(event),
        )

        self.notification_listener.deliver(event)
        expected_dict = dict.fromkeys(self.notification_listener.header)
        expected_dict["viscosity_pass"] = "PASS"
        self.assertDictEqual(
            expected_dict, self.notification_listener.row_data
        )
