import copy

from traits.api import (
    cached_property, on_trait_change, Dict, Int,
    Instance, Str, List, Property)
from traitsui.api import (
    VGroup, HGroup, UItem, View, Group, Label, Item, RangeEditor
)

from force_wfmanager.ui import BaseDataView

from surfactant_example.data_view.curve_data_table import (
    CurveTableRow, CurveDataTable)
from surfactant_example.data_view.formulation_base_table import (
    FormulationBaseTable)
from surfactant_example.data_view.subset_plot import (
    SubsetPlot
)


class FormulationDataView(BaseDataView):
    """View that allows the user to build a formulation 'base' by mapping MCO
    variables to chemical components. Only data that corresponds to the
    subset of values in the analysis model related to the formulation will
    by displayed in a scatter plot.

    In this way, users can display a 'salt curve' to investigate viscosity
    measurements for each formulation explored by the MCO
    """

    title = 'Formulation Base Data View'

    description = "Salt-curve scatter plot"

    #: MCO variable to obtain map to the salt concentration in the
    #: formulation
    salt_variable = Str

    #: MCO variable to obtain map to the formulation property under
    #: investigation (i.e. viscosity)
    curve_variable = Str

    #: Table used to define the mapping between MCO variables and formulation
    #: base components
    base_table = Instance(FormulationBaseTable)

    #: Table that lists sets of data values for each formulation base
    #: explored in the MCO
    curve_data_table = Instance(CurveDataTable)

    #: Number of decimal places to round concentration values to when building
    #: formulaton bases
    conc_rounding = Int(2)

    #: Scatter plot used to display the salt-curve data values for a selected
    #: formulation base
    curve_plot = Instance(SubsetPlot)

    #: Cached data points, based on the formulation base mappings
    _data = Dict(Str, CurveTableRow)

    #: Utility attribute to list all MCO variables in the current formulation
    #: base
    _base_variables = Property(
        List(Str), depends_on='base_table.base_variables[]'
    )

    #: Header to be displayed in the curve data table, based on user selection
    #: of plot axis
    _curve_table_header = Property(
        List(Str), depends_on='_base_variables,_curve_index'
    )

    #: Utility attribute to map the formulation variables to indices in the
    #: analysis_model header
    _base_indices = Property(
        List(Int), depends_on='_base_variables,'
                              'analysis_model:header[]')

    #: Utility attribute to map the curve variable to an index in the
    #: analysis_model header
    _curve_index = Property(
        Int, depends_on='curve_variable,'
                        'analysis_model:header[]')

    #: Utility attribute to map the salt variable to an index in the
    #: analysis_model header
    _salt_index = Property(
        Int, depends_on='salt_variable,'
                        'analysis_model:header[]')

    def default_traits_view(self):
        return View(
            HGroup(
                VGroup(
                    Label('Select the variables to be displayed'
                          'in the salt-curve plot'),
                    UItem("curve_plot", style='custom')
                ),
                VGroup(
                    Group(
                        UItem("base_table",
                              style='custom',
                              resizable=False),
                        scrollable=True,
                        show_border=True),
                    Label("Select a formulation base to view in the"
                          " salt-curve plot"),
                    HGroup(
                        Item('conc_rounding',
                             editor=RangeEditor(
                                 low=0, high=10,
                                 high_label='No. of decimal places'),
                             label="Concentration rounding",
                             tooltip="Number of decimal places to round"
                                     " concentration values")
                    ),
                    UItem("curve_data_table", style='custom'),
                ),
                scrollable=True
            )
        )

    def _curve_plot_default(self):
        """Returns a curve plot with synced variables for the axis
        on display.
        """
        curve_plot = SubsetPlot(
            title='Salt Curve',
            analysis_model=self.analysis_model,
            is_active_view=self.is_active_view
        )
        self.sync_trait("is_active_view", curve_plot)
        self.sync_trait("salt_variable", curve_plot, alias='x')
        self.sync_trait("curve_variable", curve_plot, alias='y')

        return curve_plot

    def _curve_data_table_default(self):
        """Returns a table with columns formatted to display the variables
        in the formulation base and selected as the curve
        """
        curve_data_table = CurveDataTable(
            header=self._curve_table_header
        )
        return curve_data_table

    def _base_table_default(self):
        return FormulationBaseTable()

    @cached_property
    def _get__base_variables(self):
        return self.base_table.base_variables

    @cached_property
    def _get__base_indices(self):
        try:
            return [
                self.analysis_model.header.index(variable)
                for variable in self._base_variables
            ]
        except (ValueError, IndexError):
            return []

    @cached_property
    def _get__curve_index(self):
        try:
            return self.analysis_model.header.index(
                self.curve_variable
            )
        except (ValueError, IndexError):
            return None

    @cached_property
    def _get__salt_index(self):
        try:
            return self.analysis_model.header.index(
                self.salt_variable
            )
        except (ValueError, IndexError):
            return None

    @cached_property
    def _get__curve_table_header(self):
        header = copy.copy(self._base_variables)
        if self._curve_index is not None:
            header.append(
                self.analysis_model.header[self._curve_index])
        return header

    @on_trait_change("analysis_model.header[],"
                     "is_active_view")
    def request_update(self):
        # Listens to the change in data points in the analysis model.
        # Enables the plot update at the next cycle.
        self._update_displayable_value_names()
        if self.analysis_model.is_empty:
            self._reset_data_view()
            self.base_table.table_rows = []

    @on_trait_change('displayable_value_names,'
                     'curve_variable,salt_variable')
    def _update_available_variables(self):
        """Updates the list of available variables that can be mapped
        to formulation base components
        """
        if self.analysis_model is None:
            available = []
        else:
            available = list(self.analysis_model.header)
            if self.curve_variable in available:
                available.remove(self.curve_variable)
            if self.salt_variable in available:
                available.remove(self.salt_variable)

        self.base_table.available = available

    @on_trait_change('_base_variables,_curve_index,conc_rounding')
    def _initialize_data(self):
        """Initializes the cached data values for each formulation base"""

        self.analysis_model.selected_step_indices = None

        if len(self._base_variables) == 0:
            self._reset_data_view()
            return

        self.curve_data_table.header = self._curve_table_header
        data = {}
        for index, _ in enumerate(
                self.analysis_model.evaluation_steps):
            self._record_max_value_for_entry(index, data)

        self._data = data
        self.curve_data_table.selected_row = None
        self.curve_data_table.table_rows = list(self._data.values())

    @on_trait_change("analysis_model:evaluation_steps[]", post_init=True)
    def _update_data(self):
        """Updates the cached data values for each formulation base"""
        if self.analysis_model.is_empty:
            self._reset_data_view()
            self.base_table.table_rows = []
        else:
            self._record_max_value_for_entry(-1, self._data)
        self.curve_data_table.table_rows = list(self._data.values())

    @on_trait_change('curve_data_table.selected_row')
    def _update_curve_plot(self):
        """Updates the data displayed in the curve plot, depending on the
        selected formulation base row
        """
        if self.curve_data_table.selected_row is not None:
            self.curve_plot.evaluation_indices = (
                self.curve_data_table.selected_row.evaluation_indices
            )
        else:
            self.curve_plot.evaluation_indices = []

    def _reset_data_view(self):
        self._data = {}
        self.curve_data_table.selected_row = None
        self.curve_data_table.header = []
        self.curve_data_table.table_rows = []

    def _format_data_value(self, value):
        try:
            return round(value, self.conc_rounding)
        except TypeError:
            return value

    def _format_data_hash_key(self, data_entry):
        """Generates a hash key based on the components of the
        formulation base. This is used to cache data from the MCO"""
        return '-'.join([
            ':'.join([self.analysis_model.header[index],
                      str(self._format_data_value(data_entry[index]))])
            for index in self._base_indices])

    def _record_max_value_for_entry(self, index, data):
        """Updates the cached data for the formulation base from a
        evaluation data point in the analaysis_model."""

        if self._curve_index is None:
            return

        # Obtain data in analysis model and generate hash key based
        # on formulation base mappings
        entry = self.analysis_model.evaluation_steps[index]
        key = self._format_data_hash_key(entry)

        # Identify the variable value designated as the curve data
        curve_value = entry[self._curve_index]

        if key in data:
            # Update the cache if the formulation base has been
            # explored before
            data[key].curve_max = max(
                [curve_value, data[key].curve_max]
            )
            data[key].evaluation_indices.append(index)
        else:
            # Create a new entry in the cache that records the maximum
            # curve value to display in the table and the analysis data
            # index to pass on to the curve scatter plot
            table_row = CurveTableRow(
                curve_max=curve_value,
                evaluation_indices=[index]
            )
            for index, variable in zip(self._base_indices,
                                       self._base_variables):
                table_row.add_trait(
                    variable, self._format_data_value(entry[index])
                )
            data[key] = table_row
