
import unittest
from unittest.mock import patch, MagicMock
import os
import pickle
import shutil

class TestFaceEncoding(unittest.TestCase):
    @patch('face_recognition.load_image_file')
    @patch('face_recognition.face_encodings')
    def test_face_encoding_saves_pickle(self, mock_encodings, mock_load_image):
        # Setup mocks
        mock_load_image.return_value = 'fake_image_data'
        mock_encodings.return_value = [[0.1, 0.2, 0.3]]
        
        # Simulate directory and file structure
        test_data_dir = 'tests/mock_data/person1'
        os.makedirs(test_data_dir, exist_ok=True)
        test_img_path = os.path.join(test_data_dir, 'test.jpg')
        with open(test_img_path, 'w') as f:
            f.write('fake')
        
        # Patch os.listdir and isdir
        with patch('os.listdir', side_effect=[["person1"], ["test.jpg"]]), \
             patch('os.path.isdir', return_value=True):
            import save_encodings
            # Check if encodings file is created
            self.assertTrue(os.path.exists('encodings/face_encodings.pkl'))
            with open('encodings/face_encodings.pkl', 'rb') as f:
                encodings, names = pickle.load(f)
                self.assertEqual(names, ["person1"])
                self.assertEqual(encodings, [[0.1, 0.2, 0.3]])
        # Cleanup
        if os.path.exists(test_img_path):
            os.remove(test_img_path)
        # Remove the mock_data directory tree safely
        mock_data_root = 'tests/mock_data'
        if os.path.exists(mock_data_root):
            shutil.rmtree(mock_data_root)
        if os.path.exists('encodings/face_encodings.pkl'):
            os.remove('encodings/face_encodings.pkl')

if __name__ == '__main__':
    unittest.main()
