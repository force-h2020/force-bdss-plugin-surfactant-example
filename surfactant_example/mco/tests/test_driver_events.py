from unittest import TestCase

from surfactant_example.mco.driver_events import (
    IngredientProgressEvent,
    KPIProgressEvent,
    SurfactantMCOStartEvent,
)


class TestDriverEvents(TestCase):

    def test_getstate_ingredient_progress_event(self):
        event = IngredientProgressEvent(
            name="ingredient_name", role="ingredient_role"
        )
        self.assertDictEqual(
            event.__getstate__(),
            {
                "id": "surfactant_example.mco.driver_events"
                      ".IngredientProgressEvent",
                "model_data":
                    {
                        "name": "ingredient_name",
                        "role": "ingredient_role"
                    }
            }
        )

    def test_getstate_kpi_progress_event(self):
        event = KPIProgressEvent(value="FAIL")
        self.assertDictEqual(
            event.__getstate__(),
            {
                "id": "surfactant_example.mco.driver_events"
                      ".KPIProgressEvent",
                "model_data": {"name": "", "value": "FAIL"}
            }
        )

    def test_getstate_start_event(self):
        event = SurfactantMCOStartEvent(
            parameter_names=["p1", "p2", "p3"], kpi_names=["kpi"]
        )
        self.assertDictEqual(
            event.__getstate__(),
            {
                "id": "surfactant_example.mco.driver_events"
                      ".SurfactantMCOStartEvent",
                "model_data": {
                    "parameter_names": ["p1", "p2", "p3"],
                    "kpi_names": ["kpi"]
                }
            }
        )
        self.assertEqual(
            ["p1", "p2", "p3", "kpi", "kpi_pass"], event.serialize()
        )
