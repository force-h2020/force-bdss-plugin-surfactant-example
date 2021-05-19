from unittest import TestCase, mock

from .. gromacs_database import GromacsDatabase, MissingFragmentException


class TestGromacsDatabase(TestCase):

    def setUp(self):
        self.gromacs_database = GromacsDatabase()

    def test_data(self):

        self.assertIsNotNone(self.gromacs_database.file_path)
        self.assertIsNotNone(self.gromacs_database._data)
        self.assertListEqual(
            ["Sodium Dodecyl Sulfate", "Dodecyl Phosphocholine",
             "Sodium Laureth Sulfate 1",
             "Sodium Laureth Sulfate 2",
             "Sodium Laureth Sulfate 3", "Sodium Chloride",
             "Water"],
            list(self.gromacs_database._data.keys())
        )

    def test_missing_fragment(self):

        with mock.patch(
                'force_gromacs.api'
                '.GromacsMoleculeReader.read') as mock_read:
            mock_read.return_value = []

            with self.assertRaises(MissingFragmentException):
                self.gromacs_database.get_fragment(
                    'some-topology.itp', 'Water')

    def test_get_ingredient(self):

        water = self.gromacs_database.get_ingredient('Water')

        self.assertEqual("Water", water.name)
        self.assertEqual("Solvent", water.role)
        self.assertEqual(72.05952, water.mass)
        self.assertEqual(1, len(water.fragments))
        self.assertEqual(1, len(self.gromacs_database._fragment_cache))

        salt = self.gromacs_database.get_ingredient('Sodium Chloride')

        self.assertEqual("Sodium Chloride", salt.name)
        self.assertEqual("Salt", salt.role)
        self.assertAlmostEqual(58.44280, salt.mass)
        self.assertEqual(2, len(salt.fragments))
        self.assertEqual(3, len(self.gromacs_database._fragment_cache))

    def test_get_role(self):

        surfactants = self.gromacs_database.get_role('Surfactant')

        self.assertEqual(5, len(surfactants))
        self.assertEqual(6, len(self.gromacs_database._fragment_cache))

        self.assertEqual("Sodium Dodecyl Sulfate", surfactants[0].name)
        self.assertEqual("Surfactant", surfactants[0].role)
        self.assertEqual(288.3794, surfactants[0].mass)
        self.assertEqual(2, len(surfactants[0].fragments))

        self.assertEqual("Dodecyl Phosphocholine", surfactants[1].name)
        self.assertEqual("Surfactant", surfactants[1].role)
        self.assertEqual(314.3422, surfactants[1].mass)
        self.assertEqual(1, len(surfactants[1].fragments))

        self.assertEqual("Sodium Laureth Sulfate 1", surfactants[2].name)
        self.assertEqual("Surfactant", surfactants[2].role)
        self.assertEqual(332.3794, surfactants[2].mass)
        self.assertEqual(2, len(surfactants[2].fragments))

        self.assertEqual("Sodium Laureth Sulfate 2", surfactants[3].name)
        self.assertEqual("Surfactant", surfactants[3].role)
        self.assertEqual(376.3794, surfactants[3].mass)
        self.assertEqual(2, len(surfactants[3].fragments))

        self.assertEqual("Sodium Laureth Sulfate 3", surfactants[4].name)
        self.assertEqual("Surfactant", surfactants[4].role)
        self.assertEqual(420.3794, surfactants[4].mass)
        self.assertEqual(2, len(surfactants[4].fragments))
