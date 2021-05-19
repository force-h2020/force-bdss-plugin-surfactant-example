import unittest

from force_wfmanager.model.analysis_model import AnalysisModel

from surfactant_example.data_view.formulation_data_view import (
    FormulationDataView)
from surfactant_example.data_view.formulation_base_table import (
    FormulationTableRow
)


class TestFormulationBaseView(unittest.TestCase):

    def setUp(self):
        self.base_table_row = FormulationTableRow(
            chemical='parameter_1')
        self.analysis_model = AnalysisModel(
            header=['parameter_1', 'parameter_2',
                    'salt', 'kpi_1'],
            _evaluation_steps=[('A', 1.45, 0.5, 10),
                               ('A', 5.11, 1.0, 12),
                               ('B', 4.999, 1.1, 17),
                               ('B', 4.998, 2.0, 22)]
        )
        self.data_view = FormulationDataView(
            analysis_model=self.analysis_model
        )

    def test_base_table_row_variables(self):
        self.assertListEqual(
            ['parameter_1'], self.base_table_row.variables)

        self.base_table_row.concentration = 'conc_1'
        self.assertListEqual(
            ['parameter_1', 'conc_1'],
            self.base_table_row.variables)

    def test_base_variables(self):
        self.assertEqual([], self.data_view._base_variables)

        self.data_view.base_table.table_rows = [
            self.base_table_row,
            FormulationTableRow(chemical='parameter_2')
        ]
        self.assertListEqual(
            ['parameter_1', 'parameter_2'],
            self.data_view._base_variables
        )

    def test_base_indices(self):
        self.assertEqual([], self.data_view._base_indices)

        self.data_view.base_table.table_rows = [self.base_table_row]
        self.assertEqual([0], self.data_view._base_indices)

        self.data_view.base_table.table_rows.append(
            FormulationTableRow(chemical='parameter_2'))
        self.assertEqual([0, 1], self.data_view._base_indices)

    def test_salt_curve_index(self):
        self.assertEqual('', self.data_view.curve_variable)
        self.assertIsNone(self.data_view._curve_index)

        self.data_view.curve_variable = 'kpi_1'
        self.assertEqual(3, self.data_view._curve_index)

        self.assertEqual('', self.data_view.salt_variable)
        self.assertIsNone(self.data_view._salt_index)

        self.data_view.salt_variable = 'salt'
        self.assertEqual(2, self.data_view._salt_index)

    def test_format_data_value(self):
        self.assertEqual(
            'a string', self.data_view._format_data_value('a string'))
        self.assertEqual(
            1.0, self.data_view._format_data_value(0.999))

        self.data_view.conc_rounding = 4
        self.assertEqual(
            0.999, self.data_view._format_data_value(0.999))

    def test_format_data_hash_key(self):
        self.assertEqual(
            '',
            self.data_view._format_data_hash_key(
                ('A', 1.45, 0.5, 10))
        )

        self.data_view.base_table.table_rows = [self.base_table_row]
        self.assertEqual(
            'parameter_1:A',
            self.data_view._format_data_hash_key(
                ('A', 1.45, 0.5, 10))
        )

        self.base_table_row.concentration = 'parameter_2'
        self.data_view.base_table.table_rows = [self.base_table_row]
        self.assertEqual(
            'parameter_1:A-parameter_2:1.46',
            self.data_view._format_data_hash_key(
                ('A', 1.4566, 0.5, 10))
        )

        self.analysis_model.header = []
        self.assertEqual(
            '',
            self.data_view._format_data_hash_key(
                ('A', 1.45, 0.5, 10))
        )

    def test_initialize_data(self):
        data_table = self.data_view.curve_data_table
        self.data_view.curve_variable = 'kpi_1'
        self.data_view.salt_variable = 'salt'
        self.data_view.base_table.table_rows = [
            self.base_table_row,
            FormulationTableRow(chemical='parameter_2')
        ]

        for key in ['parameter_1:A-parameter_2:1.45',
                    'parameter_1:A-parameter_2:5.11',
                    'parameter_1:B-parameter_2:5.0']:
            self.assertIn(key, self.data_view._data)
        self.assertIsNone(data_table.selected_row)

        data_table.selected_row = data_table.table_rows[0]
        self.data_view.conc_rounding = 1
        for key in ['parameter_1:A-parameter_2:1.4',
                    'parameter_1:A-parameter_2:5.1',
                    'parameter_1:B-parameter_2:5.0']:
            self.assertIn(key, self.data_view._data)
        self.assertIsNone(data_table.selected_row)

    def test_update_data(self):
        self.data_view.curve_variable = 'kpi_1'
        self.data_view.salt_variable = 'salt'
        self.data_view.base_table.table_rows = [self.base_table_row]

        self.assertEqual(2, len(self.data_view._data))
        table_row = self.data_view._data['parameter_1:A']
        self.assertEqual(12, table_row.curve_max)

        self.analysis_model.header = []
        self.assertEqual(0, len(self.data_view._data))

    def test_record_max_value_for_entry(self):
        self.data_view.curve_variable = 'kpi_1'
        self.data_view.salt_variable = 'salt'
        self.data_view.base_table.table_rows = [self.base_table_row]

        data = {}
        self.data_view._record_max_value_for_entry(0, data)
        self.assertEqual(1, len(data))
        self.assertIn('parameter_1:A', data)

        table_row = data['parameter_1:A']
        self.assertEqual(10, table_row.curve_max)
        self.assertEqual('A', table_row.parameter_1)
