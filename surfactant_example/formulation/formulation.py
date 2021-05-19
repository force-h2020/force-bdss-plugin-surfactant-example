import numpy as np

from traits.api import HasTraits, Property, List, Float, Unicode

from surfactant_example.ingredient.ingredient import Ingredient


class Formulation(HasTraits):

    # List of constituent chemical Ingredient objects
    ingredients = List(Ingredient)

    # List of concentrations by mass % for each Ingredient
    concentrations = List(Float)

    # List of corresponding number fractions for each Ingredient
    num_fractions = Property(List(Float),
                             depends_on='ingredients.mass,concentrations')

    # Total price of formulation in $USD / kg
    price = Property(Float, depends_on='ingredients.price,concentrations')

    # Formulation reference key for each experiment
    ref = Property(Unicode, depends_on='ingredients.fragments.symbol')

    def _get_num_fractions(self):
        masses = [
            ingredient.mass for ingredient in self.ingredients
        ]
        return calculate_num_fractions(masses, self.concentrations)

    def _get_price(self):
        prices = [
            ingredient.price for ingredient in self.ingredients
        ]
        return calculate_price(prices, self.concentrations)

    def _get_ref(self):
        """Generate reference for formulation based on ingredient
        concentrations and fragment symbols"""
        reference = []
        for concentration, ingredient in zip(
                self.concentrations, self.ingredients):
            if ingredient.role != 'Solvent':
                for fragment in ingredient.fragments:
                    reference.append(fragment.symbol.lower())
                reference.append(str(round(concentration, 2)))

        return '-'.join(reference)

    def fragment_search(self, symbols):
        """From a list of given symbols, return a list of
        Fragment objects from each Ingredient that have matching
        symbols. If a Fragment with the same symbol exists in
        multiple Ingredients, then they are expected to provide
        redundant information, so only return one instance
        for reference."""

        fragments = {}
        for ingredient in self.ingredients:
            for fragment in ingredient.fragments:
                if (fragment.symbol in symbols
                        and fragment.symbol not in fragments):
                    fragments[fragment.symbol] = fragment

        return list(fragments.values())

    def ingredient_search(self, roles):
        """From a list of given roles, return a list of all
        Ingredient objects that have matching roles"""

        ingredients = []
        for ingredient in self.ingredients:
            if (ingredient.role in roles
                    and ingredient not in ingredients):
                ingredients.append(ingredient)

        return ingredients


def calculate_price(prices, concentrations):
    """
    From a list of prices in $USD / kg and concentrations in mass %,
    calculate the price of the formulation in $USD / kg
    """

    # Normalise ingredient concentrations
    concentrations = np.asarray(concentrations) / np.sum(concentrations)

    # Calculate all ingredient price * conc weights
    price_conc = prices * concentrations

    return sum(price_conc)


def calculate_num_fractions(masses, concentrations):
    """
    From a list of masses and concentrations, calculate the number
    fractions of each element as a numpy array.

    Notes
    -----

    These number fractions are derived from the following relationships:

    .. math::
        c_a = \\frac{N_a m_a}{\\sum N_i m_i}

    using :math:`\\alpha = \\sum N_i m_i`,

    .. math::
        N_a = \\alpha\\frac{c_a}{m_a}

        \\sum N_i = \\alpha \\sum \\frac{c_i}{m_i}

    and by inspection,

    .. math::
        \\frac{N_a}{\\sum N_i} =
        \\frac{{\\frac{c_a}{m_a}}}{{\\sum \\frac{c_i}{m_i}}}

    """

    # Normalise ingredient concentrations
    concentrations = np.asarray(concentrations) / np.sum(concentrations)

    # Calculate all ingredient conc / mass ratios
    mass_conc = concentrations / np.asarray(masses)
    total_mass_conc = np.sum(mass_conc)

    # Number fraction of each ingredient is represented as a fraction
    # out of sum of all conc / mass ratios
    num_fracs = mass_conc / total_mass_conc

    return num_fracs
