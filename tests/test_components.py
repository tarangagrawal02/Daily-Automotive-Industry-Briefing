import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_history.db"
        self.db = Database(self.test_db_path)
        
    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_insert_and_retrieve(self):
        self.db.insert_story(
            date="2023-10-20T10:00:00",
            headline="Test Headline",
            company="Test Co",
            topic="Testing",
            geography="Global",
            source="Test Source",
            url="http://example.com/test",
            key_facts="[]",
            strategic_theme="Test Theme"
        )
        
        # URL should be processed
        self.assertTrue(self.db.is_url_processed("http://example.com/test"))
        self.assertFalse(self.db.is_url_processed("http://example.com/other"))
        
if __name__ == "__main__":
    unittest.main()
