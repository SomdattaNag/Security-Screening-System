
import unittest
from unittest.mock import patch, MagicMock
import numpy as np


class TestAccessoryDetection(unittest.TestCase):
    @patch('main.torch.hub.load')
    def test_detect_accessories(self, mock_yolo_load):
        # Mock YOLO model output
        mock_model = MagicMock()
        mock_model.names = ["mask", "sunglasses", "cap", "scarf-kerchief"]
        mock_model.return_value.xyxy = [np.array([[0,0,10,10,0.9,0]])]
        mock_model.return_value.names = ["mask"]
        mock_yolo_load.return_value = mock_model

        from main import SecuritySystem
        system = SecuritySystem()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        try:
            result = system.detect_accessories(frame)
        except Exception as e:
            self.fail(f"detect_accessories raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()
