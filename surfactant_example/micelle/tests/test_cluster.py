from unittest import TestCase

import numpy as np

from surfactant_example.micelle.cluster import (
    molecular_criteria, cluster, label_elements,
    label_set)


class LabelTestCase(TestCase):

    def setUp(self):

        # Matrix refers to a system containing 2 clusters: one
        # with particles 0, 1, 2 and 6, and the other with
        # particles 3, 4 and 5.
        self.matrix = np.array([[0, 1, 0, 0, 0, 0, 1],
                                [1, 0, 1, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 1, 1, 0],
                                [0, 0, 0, 1, 0, 1, 0],
                                [0, 0, 0, 1, 1, 0, 0],
                                [1, 0, 0, 0, 0, 0, 0]])

        self.labels = np.array([1, 1, 1, 2, 2, 2, 1])

        # Matrix refers to a system containing 3 clusters: one
        # with particles 0, 1, 2, 3, 9 and 10 another with
        # particles 6, 7 and 8, and the last with particles
        # 4 and 5.
        self.large_matrix = np.array(
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
             [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
             [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

        self.large_labels = np.array([1, 1, 1, 2, 2, 1,
                                      3, 1, 3, 1, 3, 1])

        # Matrix refers to a system where all particles
        # are connected, but ordering of assignment is difficult
        self.single_cluster = np.array(
            [[0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]])

        self.single_cluster_labels = np.ones(12)

    def test_label_set(self):

        values = label_set(self.labels)
        self.assertTrue(
            np.allclose(np.array([1, 2]), values)
        )

        values = label_set(self.large_labels)
        self.assertTrue(
            np.allclose(np.array([1, 2, 3]), values))

        values = label_set(self.large_labels, 1)
        self.assertTrue(
            np.allclose(np.array([2, 3]), values))

    def test_label_elements(self):

        labels = label_elements(self.matrix.copy())
        self.assertTrue(np.allclose(self.labels, labels))

        labels = label_elements(self.matrix.copy(), noise_thresh=2)
        self.assertTrue(np.allclose(
            np.array([1, 1, 0, 2, 2, 2, 0]), labels))

        labels = label_elements(self.matrix.copy(), noise_thresh=1,
                                cluster_thresh=4)
        self.assertTrue(np.allclose(
            np.array([1, 1, 1, 0, 0, 0, 1]), labels))

        labels = label_elements(self.large_matrix.copy())
        self.assertTrue(np.allclose(self.large_labels, labels))

        labels = label_elements(self.large_matrix.copy(), noise_thresh=2)
        self.assertTrue(np.allclose(
            np.array([0, 1, 0, 0, 0, 1,
                      2, 1, 2, 1, 2, 0]), labels))

        labels = label_elements(self.large_matrix.copy(), noise_thresh=2,
                                cluster_thresh=4)
        self.assertTrue(np.allclose(
            np.array([0, 1, 0, 0, 0, 1,
                      0, 1, 0, 1, 0, 0]), labels))

        labels = label_elements(self.single_cluster.copy())
        self.assertTrue(np.allclose(self.single_cluster_labels, labels))

        labels = label_elements(self.single_cluster.copy(), noise_thresh=2)
        self.assertTrue(np.allclose(self.single_cluster_labels, labels))

        labels = label_elements(self.single_cluster.copy(), noise_thresh=3)
        self.assertTrue(np.allclose(
            np.array([0, 0, 1, 0, 0, 0,
                      0, 2, 0, 0, 0, 0]), labels))

        labels = label_elements(self.single_cluster.copy(), noise_thresh=3,
                                cluster_thresh=2)
        self.assertTrue(np.allclose(np.zeros(12), labels))


class ClusterTestCase(TestCase):

    def setUp(self):

        self.mol_ref = ['1PS', '1PS', '2PS', '2PS', '1NA']
        self.coord = np.array([[0, 0, 0],
                               [1, 1, 1],
                               [4, 4, 4],
                               [5, 5, 5],
                               [2, 0, 2]])

        self.cell_dim = np.array([6, 6, 6])

        self.d_matrix = np.asarray([[[0., 0., 0.],
                                   [-1., -1., -1.],
                                   [2., 2., 2.],
                                   [1., 1., 1.],
                                   [-2., 0., -2]],

                                  [[1, 1, 1],
                                   [0., 0., 0.],
                                   [3, 3, 3],
                                   [2, 2, 2],
                                   [-1, 1, -1]],

                                  [[-2, -2, -2],
                                   [-3, -3, -3],
                                   [0., 0., 0.],
                                   [-1, -1, -1.],
                                   [2, -2, 2]],

                                  [[-1, -1, -1],
                                   [-2, -2, -2],
                                   [1, 1, 1],
                                   [0, 0, 0.],
                                   [-3, -1, -3]],

                                  [[2, 0, 2],
                                   [1, -1, 1],
                                   [-2, 2, -2.],
                                   [3, 1, 3.],
                                   [0., 0., 0.]]])

        self.r2_matrix = np.array([[0, 3, 12, 3, 8],
                                   [3, 0, 27, 12, 3],
                                   [12, 27, 0, 3, 12],
                                   [3, 12, 3, 0, 19],
                                   [8, 3, 12, 19, 0]])

    def test_cluster_molecular(self):

        labels = cluster(self.coord, self.cell_dim, 1.0)
        self.assertEqual(0, len(label_set(labels)))

        labels = cluster(self.coord, self.cell_dim, 1.0,
                         background=-1)
        self.assertEqual(0, len(label_set(labels, -1)))

        labels = cluster(self.coord, self.cell_dim, 1.74)
        self.assertEqual(1, len(label_set(labels)))
        self.assertTrue(np.allclose(
            np.array([1, 1, 1, 1, 1]), labels)
        )

    def test_cluster_atomic(self):

        labels = cluster(self.coord[:-1], self.cell_dim, 1.74,
                         method='atomic', mol_ref=self.mol_ref[:-1])
        self.assertTrue(np.allclose(
            np.array([1, 1]), labels)
        )

        labels = cluster(self.coord, self.cell_dim, 1.74,
                         method='atomic', mol_ref=self.mol_ref)
        self.assertTrue(np.allclose(
            np.array([1, 1, 1]), labels)
        )

    def test_molecular_criteria(self):
        mol_ref = ['1PS', '1PS', '1PS', '2PS', '2PS', '2PS']
        matrix = np.array([[0, 1, 1, 0, 0, 0],
                           [1, 0, 1, 0, 0, 0],
                           [1, 1, 0, 0, 1, 1],
                           [0, 0, 0, 0, 1, 1],
                           [0, 0, 1, 1, 0, 1],
                           [0, 0, 1, 1, 1, 0]])

        self.assertTrue(
            np.allclose(
                np.array([[0, 1],
                          [1, 0]]),
                molecular_criteria(matrix, mol_ref=mol_ref)
            )
        )

        self.assertTrue(
            np.allclose(
                np.array([[0, 1],
                          [1, 0]]),
                molecular_criteria(matrix, mol_ref=mol_ref, atom_thresh=2)
            )
        )

        self.assertTrue(
            np.allclose(
                np.array([[0, 0],
                          [0, 0]]),
                molecular_criteria(matrix, mol_ref=mol_ref, atom_thresh=3)
            )
        )

        mol_ref = ['1PS'] * 2 + ['2PS'] * 2 + ['3PS'] * 2
        mol_ref += ['1SS'] * 3 + ['2SS'] * 3
        large_matrix = np.array(
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
             [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
             [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

        self.assertTrue(
            np.allclose(
                np.array([[0, 0, 1, 0, 1],
                          [0, 0, 1, 1, 0],
                          [1, 1, 0, 1, 0],
                          [0, 1, 1, 0, 1],
                          [1, 0, 0, 1, 0]]),
                molecular_criteria(large_matrix, mol_ref=mol_ref)
            )
        )

        self.assertTrue(
            np.allclose(
                np.array([[0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 1],
                          [0, 0, 0, 1, 0]]),
                molecular_criteria(large_matrix, mol_ref=mol_ref,
                                   atom_thresh=3)
            )
        )
