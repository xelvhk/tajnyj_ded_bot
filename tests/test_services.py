import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services import services


class EventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        patcher = patch.object(services, 'DB_PATH', Path(self.temp.name) / 'db.sqlite')
        patcher.start()
        self.addCleanup(patcher.stop)
        services.start_record()

    def test_draw_is_stable_and_has_no_self_assignments(self):
        for user_id in range(1, 5):
            services.register(user_id, str(user_id))
            services.save_gift(user_id, 'gift')
        self.assertEqual(len(services.draw()), 4)
        before = [services.assignment(i) for i in range(1, 5)]
        self.assertEqual(services.draw(), [])
        self.assertEqual(before, [services.assignment(i) for i in range(1, 5)])
        recipients = [int(row[1]) for row in before]
        self.assertEqual(set(recipients), set(range(1, 5)))
        self.assertTrue(all(i != recipient for i, recipient in enumerate(recipients, 1)))
        self.assertEqual(services.register(5, 'late'), 'closed')

    def test_requires_two_ready_users_and_rejects_unknown_gift(self):
        self.assertFalse(services.save_gift(99, 'gift'))
        services.register(1, 'one')
        services.save_gift(1, 'gift')
        self.assertEqual(services.draw(), [])
        self.assertEqual(services.status(), (1, 1, 0))
