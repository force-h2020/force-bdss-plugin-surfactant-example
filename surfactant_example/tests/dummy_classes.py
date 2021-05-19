from surfactant_example.chemical.chemical_data_source import Chemical


class DummyChemical(Chemical):

    def __init__(self, name='Dummy', charge=0, mass=1):
        super(DummyChemical, self).__init__(
            name=name, charge=charge, price=1.0,
            mass=mass, symbol='D'
        )


class DummyCommand:
    pass


class DummyCommand_2(DummyCommand):

    def bash_script(self):
        pass


class DummyCommand_3(DummyCommand_2):

    def run(self):
        pass
