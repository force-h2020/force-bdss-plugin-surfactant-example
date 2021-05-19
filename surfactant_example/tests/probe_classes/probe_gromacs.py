from force_gromacs.api import (
    Gromacs_genbox, Gromacs_genion, GromacsPipeline,
    GromacsTopologyWriter, FileTreeBuilder
)


class ProbeGromacsPipeline(GromacsPipeline):

    def __init__(self):
        steps = [
            (
                'file_tree',
                FileTreeBuilder(
                    directory='./test_experiment',
                    folders=['1_init', '2_solvate',
                             '3_ions', '4_minimize',
                             '5_production'],
                    dry_run=False
                )
            ),
            (
                'genbox',
                Gromacs_genbox(
                    command_options={
                        '-cp': 'test_coord.gro',
                        '-nmol': 30,
                        '-o': 'test_output.gro',
                        '-not_a_flag': 60,
                        '-try': True
                    }
                )
            ),
            (
                'genion',
                Gromacs_genion(
                    command_options={
                        '-s': 'test_top.trp',
                        '-p': 'test_top.top',
                        '-pname': 'test_coord_2.gro',
                        '-np': 64,
                        '-pq': 1,
                        '-o': 'test_output.gro',
                        '-cp': 'problem'
                    }
                )
            ),
            (
                'top_file',
                GromacsTopologyWriter(
                    top_name='test_topology.top',
                    sim_name='test_experiment',
                    topologies=['test_top.itp'],
                    symbols=['S'],
                    n_mols=[30]
                )
            )
        ]

        super(ProbeGromacsPipeline, self).__init__(steps=steps)
