import unittest
from urllib.parse import urljoin
import os, requests
import json

ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')

class MessageTest(unittest.TestCase):
    def test_save_message_unregistered(self):
        job_id = "test_job"
        url = urljoin(ACCEPTANCE_URL, f'/job/{job_id}/message')
        req = requests.post(url, json='testing message')
        self.assertNotEqual(200, req.status_code)

