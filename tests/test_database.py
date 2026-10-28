
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_users.db"

        self.db_path_patcher = patch.object(
            database, "DB_PATH", self.test_db_path
        )
        self.db_path_patcher.start()

        database.initialize_database()

    def tearDown(self):
        self.db_path_patcher.stop()
        self.temp_dir.cleanup()

    def test_upsert_users_and_count(self):
        users = [
            {
                "external_id": 1,
                "full_name": "Kartik",
                "email": "kartik@example.com",
                "city": "Hyderabad",
                "phone": "1234567890",
            },
            {
                "external_id": 2,
                "full_name": "Alex",
                "email": "alex@example.com",
                "city": "Mumbai",
                "phone": "9876543210",
            },
        ]

        processed = database.upsert_users(users)

        self.assertEqual(processed, 2)
        self.assertEqual(database.get_user_count(), 2)

    def test_upsert_updates_existing_user(self):
        original_user = [{
            "external_id": 1,
            "full_name": "Kartik",
            "email": "old@example.com",
            "city": "Hyderabad",
            "phone": "1234567890",
        }]

        updated_user = [{
            "external_id": 1,
            "full_name": "Kartik",
            "email": "new@example.com",
            "city": "Hyderabad",
            "phone": "1234567890",
        }]

        database.upsert_users(original_user)
        database.upsert_users(updated_user)

        saved_users = database.get_all_users()

        self.assertEqual(database.get_user_count(), 1)
        self.assertEqual(saved_users[0]["email"], "new@example.com")


if __name__ == "__main__":
    unittest.main()
