import numpy as np


def calculate_n_mols(size, num_fractions):
    """Calculates number of molecules from simulation size
    and molecule number fractions. Will raise an error if
    a non-zero concentration is expected but the simulation
    is too small to contain atoms.
    """

    num_fractions = np.asarray(num_fractions)

    assert np.all(num_fractions >= 0) and np.all(num_fractions <= 1), (
        'Ingredient number fractions must all lie between'
        '0 and 1'
    )
    assert np.isclose(sum(num_fractions), 1), (
        'Ingredient number fractions do not add up to 1'
    )

    n_mols = np.asarray(num_fractions * size, dtype=int)

    if np.any((num_fractions > 0) * (n_mols == 0)):
        raise AssertionError(
            'Cannot have zero numbers of molecules, '
            'increase simulation size'
        )

    # Calculate any numerical errors in n_mols caused by integer
    # rounding
    delta_n = size - np.sum(n_mols)

    # Identify the highest number fraction relating to the molecule
    # being used in excess
    excess_molecule = np.argmax(num_fractions)

    # Add any difference between the target size and total n_mols
    # to the molecule in excess
    n_mols[excess_molecule] += delta_n

    return n_mols
