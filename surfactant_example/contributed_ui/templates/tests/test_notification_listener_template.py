from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    _GROMACS_PLUGIN_ID, SURFACTANT_PLUGIN_ID
)
from surfactant_example.contributed_ui.templates\
    .notification_listener_template import NotificationListenerTemplate


class TestNotificationListenerTemplate(TestCase):

    def setUp(self):

        self.listener_template = NotificationListenerTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID,
            gromacs_plugin_id=_GROMACS_PLUGIN_ID
        )

    def test_id(self):

        self.listener_template.plugin_id = 'force.bdss.surfactant.plugin.v1'
        new_id = "force.bdss.surfactant.plugin.v1.factory"
        self.assertEqual(new_id, self.listener_template.id)

        self.listener_template.gromacs_plugin_id = (
            'force.bdss.surfactant.plugin.v1')
        new_id = "force.bdss.surfactant.plugin.v1.factory"
        self.assertEqual(new_id, self.listener_template.gromacs_id)

    def test_create_hpc_writer_template(self):

        template = self.listener_template.create_hpc_writer_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.gromacs.plugin.wrapper.v0.factory.hpc_writer",
            template['id']
        )
        self.assertEqual(
            {"dry_run": False},
            template['model_data']
        )

    def test_create_csv_writer_template(self):

        template = self.listener_template.create_csv_writer_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory"
            ".surfactant_csv_writer",
            template['id']
        )
        self.assertEqual(
            {"dry_run": False},
            template['model_data']
        )

    def test_create_template(self):

        template = self.listener_template.create_template()
        self.assertEqual(2, len(template))
