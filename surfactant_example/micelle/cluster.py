import networkx as nx
import numpy as np
from scipy.sparse import spmatrix

from force_gromacs.api import batch_distance_matrix

from surfactant_example.micelle.utilities import (
    sum_filter, matrix_threshold, remove_digits
)

np_remove_digits = np.vectorize(remove_digits)


def label_set(array, background=0):
    """Returns a set of label values in array. Able to
    handle non-zero background label values"""

    array = np.asarray(array)

    # Extract non-background labels
    labels = array[np.where(array != background)]

    # Return a unique, ordered set of labels
    unique_labels = np.unique(labels)

    return unique_labels


def label_elements(matrix, noise_thresh=1, cluster_thresh=1):
    """Applies cluster labels to each non-zero entry in
    matrix via conversion into a networkx Graph object

    Parameters
    ----------
    matrix: array_like of float
        Matrix to label, consisting of zero and non-zero
        entries
    noise_thresh: int, optional, default: 1
        Lower threshold on number non-zero entries in each row
        be considered part of a cluster
    cluster_thresh: int, optional, default: 2
        Lower threshold on cluster size

    Returns
    -------
    cluster_labels: array_like of int
        Labels assigned to each row in matrix
    """

    # Create zeroed labels for each element in original matrix
    cluster_labels = np.zeros(matrix.shape[0])

    # Remove any entries from rows or columns corresponding to elements
    # considered as noise by noise_thresh
    indices = np.argwhere(matrix.sum(axis=-1) < noise_thresh).flatten()
    matrix = np.delete(matrix, indices, axis=0)
    matrix = np.delete(matrix, indices, axis=1)

    if matrix.size == 0:
        return cluster_labels

    # Type checking of matrix for transformation into networkx Graph
    if isinstance(matrix, np.ndarray):
        network = nx.from_numpy_array(matrix)

    elif isinstance(matrix, spmatrix):
        network = nx.from_scipy_sparse_matrix(matrix)

    else:
        raise TypeError(
            "Input adjacency matrix must be either a numpy array"
            "or scipy sparse matrix"
        )

    if indices.size > 0:
        # Ensure nodes correspond to the order of elements in original matrix
        old_indices = np.arange(matrix.shape[0])
        new_indices = np.delete(np.arange(cluster_labels.size), indices)
        mapping = {
            old_index: new_index
            for old_index, new_index in zip(old_indices, new_indices)
        }
        network = nx.relabel_nodes(network, mapping)

    # Extract clusters as connected graphs
    components = nx.connected_components(network)

    # Assign non-zero labels to each element in each graph
    label = 1
    for component in components:
        # Refine cluster labels to only report back those with greater than
        # cluster_thresh particles
        if len(component) >= cluster_thresh:
            cluster_labels[list(component)] = label
            label += 1

    return cluster_labels


def molecular_criteria(adjacency_matrix, mol_ref, atom_thresh=1):
    """Determines whether two molecules are considered to be connected
    by counting the number of pairwise adjacency_matrix between all of thier
    constituent atoms and checking that this value is > atom_thresh

    Parameters
    ----------
    adjacency_matrix: array_like of int
        An n x n binary matrix containing non-zero entries corresponding
        to a connenection between atom i and j
    mol_ref: list of str
        Reference symbols for each molecular species in a single
        frame
    atom_thresh: int, optional, default: 1
        Lower threshold on the number of atomic connections required for
        two molecule to be considered connected

    Returns
    -------
    adjacency_matrix: array_like of int
        An m x m binary matrix (where m = number of molecules) containing
        non-zero entries corresponding to a connection between molecule
        i and j
    """

    # Isolate unique values in mol_ref relating to different molecules
    mol_ref = np.asarray(mol_ref)
    unique_mol = []
    for ref in mol_ref:
        if ref not in unique_mol:
            unique_mol.append(ref)
    unique_mol = np.asarray(unique_mol)

    # Obtain set of symbols relating to different molecular species
    cleaned_ref = np_remove_digits(mol_ref)
    mol_set = np.unique(cleaned_ref)

    # Find indices in adjacency matrix that relate to each molecule
    mol_indices = [
        np.argwhere(np.char.find(unique_mol, ref) != -1) for ref in mol_set
    ]
    atom_indices = [np.argwhere(cleaned_ref == ref) for ref in mol_set]

    # Obtain the number and atom count of each molecular species
    n_mols = [indices.size for indices in mol_indices]
    n_sites = [indices.size // n_mol
               for indices, n_mol in zip(atom_indices, n_mols)]

    # Build an empty adjacency matrix to hold molecular neighbours
    mol_adjacency_matrix = np.zeros((np.sum(n_mols), np.sum(n_mols)))

    # Reduce adjacency_matrix matrix to n_molcules x n_molecules, with each
    # element containing the sum of all particle adjacency_matrix
    for n, atom_i, mol_i in zip(n_sites, atom_indices, mol_indices):
        for m, atom_j, mol_j in zip(n_sites, atom_indices, mol_indices):
            mol_adjacency_matrix[mol_i.flatten(), mol_j] = sum_filter(
                adjacency_matrix[atom_i.flatten(), atom_j],
                block_shape=(m, n)
            )

    # Zero elements that correspond to the molecule interacting with
    # itself
    np.fill_diagonal(mol_adjacency_matrix, 0)

    # Return a binary mask for each pairwise molecule interaction that meets
    # the threshold criteria
    mol_adjacency_matrix = np.where(
        mol_adjacency_matrix >= atom_thresh, 1, 0
    )

    return mol_adjacency_matrix


def cluster(coord, cell_dim, r_thresh=1.5, noise_thresh=1, cluster_thresh=2,
            background=0, method='molecular', atom_thresh=1, mol_ref=None,
            batch_size=50):
    """Assigns each particle in coord to a cluster based on input parameters.
    Returns a set of labels that reference which cluster each particle belongs
    to.

    Parameters
    ----------
    coord:  array_like of floats
        Positions of particles in 3 dimensions
    cell_dim:  array_like of floats
        Simulation cell dimensions in 3 dimensions
    r_thresh: float, optional, default: 1.5
        Upper threshold on radial distance to consider whether two
        particles are neighbours
    noise_thresh: int, optional, default: 1
        Lower threshold on number of neighbouring particles to
        be considered part of a cluster
    cluster_thresh: int, optional, default: 2
        Lower threshold on cluster size
    background: int, optional, default: 0
        Integer label to be considered a background value
    method: str, optional, default: 'molecular'
        Selects the method to perform the clustering, either 'molecular' or
        'atomic'.
        'molecular': Elements in coord are assumed to refer to position
        of each individual molecule.
        'atomic': Elements in coord are assumed to refer to atoms or beads
        with molecules, that are all n_site atoms in length. Each molecule is
        considered to be a neighbour of another if at least atom_thresh
        neighbours are present between constituent atoms
    atom_thresh: int, optional, default: 1
        Threshold number of atomic neighbours between a pair
        of molecules for the molecules themselves to be considered neighbours
    mol_ref: list of str, optional
        Reference symbols for each molecular species in a single
        frame
    batch_size : int, optional, default: 50
        Sample size parameter of each batch.

    Returns
    -------
    cluster_labels: array_like of int
        Labels assigning each particle in coord to a cluster
    """

    assert method in ['molecular', 'atomic']

    if method == 'atomic':
        assert isinstance(atom_thresh, int)
        assert isinstance(mol_ref, list)

    # Calculate cartesian and radial distances between particles
    # Perform this as a batch process to save memory
    r2_coord = batch_distance_matrix(coord, cell_dim,
                                     metric='sqeuclidean',
                                     batch_size=batch_size)

    # Identify particles lying within r_thresh radial distance
    adjacency_matrix = matrix_threshold(r2_coord,
                                        upper_thresh=r_thresh**2)

    if method == 'atomic':
        # Assign pairwise neighbours to atoms, and filter out
        # those pairwise molecule interactions that contain less than
        # atom_thresh particle neighbours
        adjacency_matrix = molecular_criteria(
            adjacency_matrix, mol_ref, atom_thresh=atom_thresh)

    # Assign cluster labels to any particles by generating a network
    cluster_labels = label_elements(adjacency_matrix,
                                    noise_thresh=noise_thresh,
                                    cluster_thresh=cluster_thresh)

    # Apply background value
    if background != 0:
        cluster_labels = np.where(cluster_labels == background,
                                  cluster_labels.max() + 1, cluster_labels)

        cluster_labels = np.where(cluster_labels,
                                  cluster_labels, background)

    return cluster_labels
