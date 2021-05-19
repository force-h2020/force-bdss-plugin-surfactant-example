from traits.api import (
    HasStrictTraits, List, Str, Property, cached_property)
from traitsui.api import (
    UItem, View, EnumEditor, TableEditor, ObjectColumn, Heading,
    Label
)


class FormulationTableRow(HasStrictTraits):
    """A row in the formulation base table, containing
    information for one of its chemical components. Each trait
    refers to a MCO variable that formats the chemical property
    """

    #: MCO variable that contains the chemical name of
    #: the formulation component
    chemical = Str

    #: MCO variable that contains the concentration of
    #: the formulation component
    concentration = Str

    #: List of available MCO variables to select from
    available = List(Str)

    #: Utility attribute to output the selected variables as a list
    variables = Property(
        List(Str), depends_on='chemical,concentration')

    def _get_variables(self):
        variables = []
        if self.chemical:
            variables.append(self.chemical)
        if self.concentration:
            variables.append(self.concentration)
        return variables


class FormulationBaseTable(HasStrictTraits):
    """Table where each row represents a chemical component
    in a formulation. The entire table provides mapping between
    the MCO variables to the formulation 'base'
    """

    #: Rows in the table
    table_rows = List(FormulationTableRow)

    #: List of available MCO variables to use for mapping to
    #: formulation components
    available = List(Str)

    #: Utility attribute to output the entire formulation variables
    #: as a list
    base_variables = Property(
        List(Str), depends_on='table_rows.[chemical,concentration]'
    )

    def default_traits_view(self):
        table_editor = TableEditor(
            columns=[
                ObjectColumn(name='chemical',
                             editor=EnumEditor(name='available')),
                ObjectColumn(name='concentration',
                             editor=EnumEditor(name='available'))],
            sortable=False,
            deletable=True,
            row_factory=self._row_factory,
        )
        return View(
            Heading('Formulation Mapping'),
            Label("Select the variables that correspond to each "
                  "formulation component's name and concentration"),
            UItem("table_rows", editor=table_editor),
        )

    @cached_property
    def _get_base_variables(self):
        base_vars = []
        for row in self.table_rows:
            base_vars += row.variables
        return base_vars

    def _row_factory(self):
        """When adding new rows, sync the available traits so that
        updates are propagated through to the drop down lists in each
        row
        """
        table_row = FormulationTableRow(
            available=self.available
        )
        self.sync_trait("available", table_row)
        return table_row
