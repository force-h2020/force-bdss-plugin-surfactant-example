from traits.api import (
    HasStrictTraits, Float, List, Str, Instance,
    Int, on_trait_change
)
from traitsui.api import (
    TabularEditor, UItem, TabularAdapter, View)


class CurveTableRow(HasStrictTraits):
    """Represents a row in the curve data table containing
    the maximum value for a selected variable that has been
    reported for a given formulation base
    """

    #: Maximum value of selected variable for formulation base
    curve_max = Float

    #: List of evaluation step indices in the analysis model that
    #: are attributed to the formulation base this is calculated
    #: from
    evaluation_indices = List(Int)


class CurveDataTable(HasStrictTraits):
    """Shows all combinations of data values recorded for particular
    formulation base (set of surfactants + their concentrations)
    and selected curve variable
    """

    #: Contains all columns in the table. Each column is a variable
    #: in the analysis model, with the final column corresponding
    #: to the curve variable
    header = List(Str)

    #: List of rows representing data gathered for each formulation
    #: base
    table_rows = List(CurveTableRow)

    #: Reference to the selected table row in the UI
    selected_row = Instance(CurveTableRow)

    tabular_adapter = Instance(TabularAdapter)

    def default_traits_view(self):
        """Creates a table view where each column corresponds to an
        object in the header attribute. The last column is expected
        to reference the maximum value reported in the curve
        """
        tabular_editor = TabularEditor(
            adapter=self.tabular_adapter,
            editable=False,
            selected='selected_row'
        )

        return View(
            UItem('table_rows', editor=tabular_editor, style='custom')
        )

    def _create_columns(self):
        columns = [
            (variable, variable)
            for variable in self.header[:-1]
        ]
        if len(self.header) > 0:
            columns.append(
                (f"max {self.header[-1]}", 'curve_max')
            )
        return columns

    def _tabular_adapter_default(self):
        return TabularAdapter(
            columns=self._create_columns()
        )

    @on_trait_change('header[]')
    def _update_header(self):
        self.table_rows = []
        self.tabular_adapter.columns = self._create_columns()
