#This code is to perform testing using unittest python package
import unittest

from transformer import transform_user


class TestTransformUser(unittest.TestCase):

    def test_valid_user(self):
        user = {
            "id": 1,
            "name": "Kartik",
            "email": "KARTIK@EXAMPLE.COM",
            "address": {"city": "Hyderabad"},
            "phone": "1234567890"
        }

        result = transform_user(user)

        self.assertEqual(result["external_id"], 1)
        self.assertEqual(result["full_name"], "Kartik")
        self.assertEqual(result["email"], "kartik@example.com")
        self.assertEqual(result["city"], "Hyderabad")
        self.assertEqual(result["phone"], "1234567890")
        
    def test_invalid_user_id(self):
        user = {
            "id": -1,
            "name": "Kartik",
            "email": "kartik@example.com"
        }

        with self.assertRaises(ValueError):
            transform_user(user)

    def test_missing_name(self):
        user = {
            "id": 1,
            "name": "   ",
            "email": "kartik@example.com"
        }

        with self.assertRaises(ValueError):
            transform_user(user)


if __name__ == "__main__":
    unittest.main()
