from traits.api import Bool

from force_bdss.api import (
    BaseCSVWriter,
    BaseCSVWriterFactory,
    BaseCSVWriterModel,
)

from surfactant_example.mco.driver_events import KPIProgressEvent


class SurfactantCSVWriterModel(BaseCSVWriterModel):
    """A BaseCSVWriterModel subclass with dry_run attribute
    included so as to be compatible with GromacsPipeline. All
    other functionalities are the same"""

    dry_run = Bool(True)


class SurfactantCSVWriter(BaseCSVWriter):
    def parse_kpiprogress_event(self, event):
        if event.name in self.row_data:
            return {event.name: event.value}
        return {}

    def deliver(self, event):
        if isinstance(event, KPIProgressEvent):
            self.row_data.update(self.parse_kpiprogress_event(event))
        else:
            super().deliver(event)


class SurfactantCSVWriterFactory(BaseCSVWriterFactory):
    def get_identifier(self):
        return "surfactant_csv_writer"

    def get_name(self):
        return "Surfactant CSV Writer"

    def get_listener_class(self):
        return SurfactantCSVWriter

    def get_model_class(self):
        return SurfactantCSVWriterModel
