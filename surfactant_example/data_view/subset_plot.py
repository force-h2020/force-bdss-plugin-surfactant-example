import logging

from traits.api import Int, on_trait_change, List

from force_wfmanager.ui.review.curve_scatter_plot import CurveScatterPlot

log = logging.getLogger(__name__)

_ERROR = 'Unable to interpolate curve through data points'


class SubsetPlot(CurveScatterPlot):
    """A subclass of CurvePlot that only shows a subset of data points
    from the analysis model, specified by the evaluation_indices attribute"""

    #: Subset of data points to show on the 2D scatter plot
    evaluation_indices = List(Int)

    @on_trait_change("analysis_model:header[],evaluation_indices[]")
    def request_update(self):
        """Overloaded parent method to only update the plot if the subset
        of data points to be showed changes
        """
        # Listens to the change in data points in the analysis model.
        # Enables the plot update at the next cycle.
        self.update_required = True

    def _filtered_data(self, variable):
        """Returns filtered data points for a given variable in the
        analysis model, based on the provided evaluation point indicies
        """
        data = self.analysis_model.column(variable)
        return [data[index] for index in self.evaluation_indices]

    def _update_plot_x_data(self):
        """ Update data points displayed by the x axis.
        Sets the x-`self._plot_data` to corresponding sub set of
        data in the `self.analysis_model`.
        This method is called by the `_update_plot` method during
        the callback update.
        This method is called when the `x` axis is changed.
        """
        if self.x == "" or self.analysis_model.is_empty:
            self._plot_data.set_data("x", [])
        else:
            self._plot.x_axis.title = self.x
            self._plot_data.set_data("x", self._filtered_data(self.x))

    def _update_plot_y_data(self):
        """ Update data points displayed by the y axis.
        Sets the y-`self._plot_data` to corresponding sub set of
        data in the `self.analysis_model`.
        This method is called by the `_update_plot` method during
        the callback update.
        This method is called when the `y` axis is changed.
        """
        if self.y == "" or self.analysis_model.is_empty:
            self._plot_data.set_data("y", [])
        else:
            self._plot.y_axis.title = self.y
            self._plot_data.set_data("y", self._filtered_data(self.y))

    @on_trait_change("color_by")
    def _update_color_plot(self):
        if (
            self.x == ""
            or self.y == ""
            or self.color_by is None
            or self.analysis_model.is_empty
        ):
            self._plot_data.set_data("color_by", [])
            return

        self._plot_data.set_data(
            "color_by", self._filtered_data(self.color_by))
