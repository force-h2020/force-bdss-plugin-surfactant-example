import unittest

from surfactant_example.data_view.formulation_base_table import (
    FormulationBaseTable, FormulationTableRow)


class TestFormulationBaseTable(unittest.TestCase):

    def setUp(self):
        self.table_row = FormulationTableRow(
            chemical='parameter_1',
            concentration='conc_1')
        self.base_table = FormulationBaseTable()

    def test_table_row_variables(self):
        self.assertListEqual(
            ['parameter_1', 'conc_1'],
            self.table_row.variables
        )

        self.table_row.concentration = ''
        self.assertListEqual(
            ['parameter_1'],
            self.table_row.variables)

    def test_base_variables(self):
        self.assertEqual([], self.base_table.base_variables)
        self.base_table.table_rows.append(self.table_row)

        self.assertListEqual(
            ['parameter_1', 'conc_1'],
            self.base_table.base_variables
        )

    def test_row_factory(self):
        row = self.base_table._row_factory()
        self.assertListEqual([], row.available)

        self.base_table.available = ['parameter']
        self.assertListEqual(['parameter'], row.available)
