from force_bdss.api import (
    Workflow, ExecutionLayer, BaseDriverEvent, BaseDataSource,
    BaseDataSourceModel, BaseDataSourceFactory)


class ProbeDriverEventDataSource(BaseDataSource):
    """An empty data source that can fire a BaseDriverEvent
    to an associated BaseDataSourceModel"""

    def run(self, model, parameters):
        model.notify_event()
        return True

    def slots(self, model):
        return ((), ())


class ProbeDriverEventDataSourceModel(BaseDataSourceModel):
    """An empty data source that can propagate a BaseDriverEvent"""

    def notify_event(self):
        """Creates a dummy BaseDriverEvent to be propagated
        to a ProbeDriverEventDataSourceModel
        """
        self.notify(BaseDriverEvent())


class ProbeDriverEventDataSourceFactory(BaseDataSourceFactory):
    """A factory that creates BaseDataSource classes that can
    fire and propagate BaseDriverEvent instances"""

    def get_identifier(self):
        return "probe_data_source"

    def get_name(self):
        return "Probe Data Source"

    def get_model_class(self):
        return ProbeDriverEventDataSourceModel

    def get_data_source_class(self):
        return ProbeDriverEventDataSource


class ProbeWorkflow(Workflow):

    def __init__(self, *args, **kwargs):

        kwargs.pop('mco', None)
        kwargs.pop('execution_layers', None)

        super(ProbeWorkflow, self).__init__(*args, **kwargs)

        factory = ProbeDriverEventDataSourceFactory(
            plugin={'id': 'pid', 'name': 'None'})
        self.execution_layers = [
            ExecutionLayer(
                data_sources=[
                    factory.create_model()]
            )
        ]
