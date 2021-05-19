from force_gromacs.tests.probe_classes.chemicals import ProbeGromacsFragment


data = {
    'So': {
        'elements': ['WAT'],
        'ids': ['WAT'],
        'indices': [1],
        'charges': [0],
        'masses': [18],
        'bonds': []
    },
    'PS1': {
        'elements': ['PS1', 'PS1'],
        'ids': ['PS11', 'PS12'],
        'indices': [1, 2],
        'charges': [-1, 0],
        'masses': [100, 20],
        'bonds': [(1, 2)]
    },
    'SS': {
        'elements': ['SS', 'SS'],
        'ids': ['SS1', 'SS2'],
        'indices': [1, 2],
        'charges': [0, 0],
        'masses': [80, 20],
        'bonds': [(1, 2)]
    },
    'PI': {
        'elements': ['PI'],
        'ids': ['PI'],
        'indices': [1],
        'charges': [1],
        'masses': [20],
        'bonds': []
    },
    'NI': {
        'elements': ['NI'],
        'ids': ['NI'],
        'indices': [1],
        'charges': [-1],
        'masses': [30],
        'bonds': []
    }
}


class DatabaseProbeGromacsFragment(ProbeGromacsFragment):

    database = data


class ProbePrimarySurfactant(DatabaseProbeGromacsFragment):

    def __init__(self):
        super(ProbePrimarySurfactant, self).__init__(
            name='Primary Surfactant',
            symbol='PS1',
            topology='test_surf_1.itp',
            coordinate='test_surf_1.gro')


class ProbeSecondarySurfactant(DatabaseProbeGromacsFragment):

    def __init__(self):
        super(ProbeSecondarySurfactant, self).__init__(
            name='Secondary Surfactant',
            symbol='SS',
            topology='test_surf_2.itp',
            coordinate='test_surf_2.gro')


class ProbePositiveIon(DatabaseProbeGromacsFragment):

    def __init__(self):
        super(ProbePositiveIon, self).__init__(
            name='Positive Ion',
            symbol='PI',
            topology='test_p_ion.itp',
            coordinate='test_p_ion.gro')


class ProbeNegativeIon(DatabaseProbeGromacsFragment):

    def __init__(self):
        super(ProbeNegativeIon, self).__init__(
            name='Negative Ion',
            symbol='NI',
            topology='test_n_ion.itp',
            coordinate='test_n_ion.gro')


class ProbeSolvent(DatabaseProbeGromacsFragment):

    def __init__(self):
        super(ProbeSolvent, self).__init__(
            name='Solvent',
            symbol='So',
            topology='test_solvent.itp',
            coordinate='test_solvent.gro')
