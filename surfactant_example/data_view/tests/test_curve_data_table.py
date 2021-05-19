import unittest

from surfactant_example.data_view.curve_data_table import (
    CurveDataTable, CurveTableRow)


class TestCurveDataTable(unittest.TestCase):

    def setUp(self):
        self.table_row = CurveTableRow()
        self.curve_data_table = CurveDataTable()

    def test_update_header(self):
        self.assertListEqual(
            [],
            self.curve_data_table.tabular_adapter.columns
        )
        self.curve_data_table.table_rows.append(self.table_row)
        self.curve_data_table.header = ['parameter', 'kpi']

        self.assertListEqual(
            [('parameter', 'parameter'),
             ('max kpi', 'curve_max')],
            self.curve_data_table.tabular_adapter.columns
        )
        self.assertListEqual([], self.curve_data_table.table_rows)

    def test__create_columns(self):
        columns = self.curve_data_table._create_columns()
        self.assertListEqual([], columns)

        self.curve_data_table.header = ['parameter', 'kpi']
        columns = self.curve_data_table._create_columns()
        self.assertListEqual(
            [('parameter', 'parameter'),
             ('max kpi', 'curve_max')],
            columns
        )
