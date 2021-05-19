from traits.api import Unicode

from force_bdss.api import BaseDriverEvent, MCOStartEvent


class SurfactantMCOStartEvent(MCOStartEvent):
    """ SurfactantMCOStartEvent class overloads the `serialize` method
    and introduces the KPI pass marks to the StartEvent representation.
    """

    def serialize(self):
        header = super().serialize()
        header += [f"{name}_pass" for name in self.kpi_names]
        return header


class IngredientProgressEvent(BaseDriverEvent):
    """ The IngredientDataSource class should emit this upon
    compilation of surfactant and salt names to be passed into
    a CSVWriter.
    """

    #: Name of an Ingredient object
    name = Unicode

    #: Role of an Ingredient object
    role = Unicode


class KPIProgressEvent(BaseDriverEvent):
    """ A DataSource class should emit this upon generation
    of a KPI pass mark to be passed into a CSVWriter.
    """

    #: Indicates whether the KPI passes the target threshold
    name = Unicode

    #: KPI pass mark string
    value = Unicode
