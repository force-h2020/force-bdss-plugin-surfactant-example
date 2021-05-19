import os
from unittest import TestCase, mock

from surfactant_example.data.gromacs_files.path import get_file


MOCK_DIRPATH = "surfactant_example.data.gromacs_files.path.dirpath"


class TestPath(TestCase):

    def test_get_filepath(self):
        mock_path = os.path.join('path', 'to', 'directory')
        with mock.patch(MOCK_DIRPATH) as mock_dirpath:
            mock_dirpath.return_value = mock_path

            self.assertEqual(
                os.path.join(mock_path, 'file_path'),
                get_file('file_path')
            )

            self.assertEqual(
                os.path.join(os.path.sep, 'file_path'),
                get_file(os.path.join(os.path.sep, 'file_path'))
            )
