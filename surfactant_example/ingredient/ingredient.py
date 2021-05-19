from traits.api import (
    Float, Enum, Property, Int, cached_property)
from traitsui.api import View, Item, Readonly

from force_bdss.api import DataValue
from force_gromacs.api import Molecule


class Ingredient(Molecule):
    """Class compiling all information required for each ingredient
    in a Gromacs simulation"""

    #: Role of ingredient in simulation
    role = Enum('Surfactant', 'Salt', 'Solvent')

    #: Price of Ingredient in $USD / kg
    price = Float()

    # --------------------
    #     Properties
    # --------------------

    #: Total number of atoms in ingredient molecule
    atom_count = Property(
        Int, depends_on='fragments.[atoms,stoichiometry]')

    # --------------------
    #     Listeners
    # --------------------

    def default_traits_view(self):
        """Returns a traits view with all visible UI objects. This is
        mainly used by the SurfactantContributedUI class"""
        return View(
            Readonly("name"),
            Readonly("mass"),
            Item("price")
        )

    @cached_property
    def _get_atom_count(self):
        return sum([len(fragment.atoms) * fragment.stoichiometry
                    for fragment in self.fragments])

    def get_data_values(self):
        """Return a list containing all DataValues stored in class,
        including new `price` attribute"""
        data_values = [DataValue(type="NAME", value=self.name),
                       DataValue(type="PRICE", value=self.price),
                       DataValue(type="MASS", value=self.mass)]

        return data_values
