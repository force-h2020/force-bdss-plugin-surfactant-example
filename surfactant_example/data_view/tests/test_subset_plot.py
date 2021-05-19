from unittest import TestCase

from force_wfmanager.model.analysis_model import AnalysisModel

from surfactant_example.data_view.subset_plot import (
    SubsetPlot)


class TestSubsetPlot(TestCase):

    def setUp(self):
        self.analysis_model = AnalysisModel(
            header=['parameter_1', 'parameter_2',
                    'salt', 'kpi_1'],
            _evaluation_steps=[('A', 1.45, 0.5, 10),
                               ('A', 5.11, 1.0, 12),
                               ('B', 4.999, 1.1, 17),
                               ('B', 4.998, 2.0, 22)]
        )
        self.plot = SubsetPlot(
            analysis_model=self.analysis_model
        )

    def test_filtered_data(self):
        data = self.plot._filtered_data('parameter_1')
        self.assertEqual(0, len(data))

        self.plot.evaluation_indices = [0, 2]
        data = self.plot._filtered_data('parameter_1')
        self.assertListEqual(['A', 'B'], data)

    def test_update_plot_x_data(self):
        self.assertEqual('', self.plot.x)
        self.assertEqual(0, len(self.plot._plot_data["x"]))

        self.plot.x = 'parameter_1'
        self.plot._update_plot_x_data()
        self.assertEqual(0, len(self.plot._plot_data["x"]))

        self.plot.evaluation_indices = [0, 2]
        self.plot._update_plot_x_data()
        self.assertListEqual(
            ['A', 'B'], self.plot._plot_data["x"].tolist()
        )

    def test_update_plot_y_data(self):
        self.assertEqual('', self.plot.y)
        self.assertEqual(0, len(self.plot._plot_data["y"]))

        self.plot.y = 'kpi_1'
        self.plot._update_plot_y_data()
        self.assertEqual(0, len(self.plot._plot_data["y"]))

        self.plot.evaluation_indices = [0, 2]
        self.plot._update_plot_y_data()
        self.assertListEqual(
            [10, 17], self.plot._plot_data["y"].tolist()
        )

    def test_update_color_plot(self):
        self.assertEqual('', self.plot.x)
        self.assertEqual('', self.plot.y)
        self.assertIsNone(self.plot.color_by)
        self.plot._check_scheduled_updates()

        self.assertEqual(0, len(self.plot._plot_data["color_by"]))

        self.plot.color_by = 'kpi_1'
        self.plot._update_color_plot()
        self.assertEqual(0, len(self.plot._plot_data["color_by"]))

        self.plot.evaluation_indices = [0, 2]
        self.plot._update_color_plot()
        self.assertListEqual(
            [10, 17], self.plot._plot_data["color_by"].tolist()
        )
