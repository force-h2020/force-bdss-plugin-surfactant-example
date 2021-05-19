import json

from traits.api import HasStrictTraits, Dict, Property, Unicode

from force_gromacs.api import GromacsMoleculeReader
from force_gromacs.data_sources.fragment.fragment_data_source import (
    MissingFragmentException
)

from surfactant_example.ingredient.ingredient import Ingredient

from .gromacs_files.path import get_file


class GromacsDatabase(HasStrictTraits):
    """Class that can perform query and parse a JSON file containing
    serialised representations of Ingredient objects"""

    #: File path for JSON containing database of Gromacs objects
    file_path = Unicode()

    #: Reader for Gromacs .itp molecule files
    _reader = GromacsMoleculeReader()

    #: Cache for storing loaded fragments
    _fragment_cache = Dict()

    #: Parsed data from JSON database
    _data = Property(Dict, depends_on='file_path')

    def _file_path_default(self):
        return get_file("chemical_database.json")

    def _get__data(self):
        """Update _data attribute if new file path defined"""
        return self._load_data(self.file_path)

    def _load_data(self, file_path):
        """Load JSON file containing chemical Ingredient data"""
        with open(file_path, 'r') as infile:
            data = json.load(infile)
        return data

    def _parse_fragment_data(self, data):
        """Parse a dictionary containing fragment data
        to provide absolute file paths"""

        for fragment in data:
            fragment["topology"] = get_file(fragment['topology'])
            fragment["coordinate"] = get_file(fragment['coordinate'])

    def get_fragment(self, topology, symbol, **kwargs):
        """Retrieve required GromacsFragment from topology
        file and update attributes

        Parameters
        ----------
        topology: str
            File path of Gromacs '.itp' file containing
            fragment data
        symbol: str
            Symbol corresponging to target fragment in
            topology file

        Returns
        -------
        fragment: GromacsFragment
            Container class with fragment information

        Raises
        ------
        MissingFragmentException: if no GromacsFragment with
        matching `symbol` atribute is loaded from topology
        file"""

        fragments = self._reader.read(topology)

        # Identify fragment loaded from Gromacs molecule
        # file and update attributes with those from database
        for fragment in fragments:
            if fragment.symbol == symbol:
                # Update fragment in file with additional
                # attribute data
                for key, value in kwargs.items():
                    setattr(fragment, key, value)
                return fragment

        raise MissingFragmentException

    def get_ingredient(self, name):
        """Return an Ingredient instance from data that is obtained
        using the name argument as a query"""

        ingredient_data = self._data[name]
        fragment_data = ingredient_data.pop("fragments", None)
        self._parse_fragment_data(fragment_data)

        ingredient_fragments = []
        for kwargs in fragment_data:
            try:
                fragment = self._fragment_cache[kwargs['symbol']]
            except KeyError:
                fragment = self.get_fragment(**kwargs)
                self._fragment_cache[fragment.symbol] = fragment
            ingredient_fragments.append(fragment)

        ingredient = Ingredient(
            name=name,
            fragments=ingredient_fragments,
            **ingredient_data
        )

        return ingredient

    def get_role(self, role):
        """Return a list of Ingredient instance from data that have
        a matching role attribute as input argument"""

        ingredients = []
        for key, value in self._data.items():
            if value['role'] == role:
                ingredients.append(self.get_ingredient(key))

        return ingredients
