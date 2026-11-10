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
        token = services.preview(10, 'draw')
        self.assertEqual(len(services.draw(10, token)), 4)
        before = [services.assignment(i) for i in range(1, 5)]
        self.assertEqual(services.draw(10, token), [])
        self.assertEqual(before, [services.assignment(i) for i in range(1, 5)])
        recipients = [int(row[1]) for row in before]
        self.assertEqual(set(recipients), set(range(1, 5)))
        self.assertTrue(all(i != recipient for i, recipient in enumerate(recipients, 1)))
        self.assertEqual(services.register(5, 'late'), 'closed')

    def test_requires_two_ready_users_and_rejects_unknown_gift(self):
        self.assertFalse(services.save_gift(99, 'gift'))
        services.register(1, 'one')
        services.save_gift(1, 'gift')
        token = services.preview(10, 'draw')
        self.assertEqual(services.draw(10, token), [])
        self.assertEqual(services.status(), (1, 1, 0))

    def test_new_game_archives_assignments_and_allows_registration(self):
        for user_id in (1, 2):
            services.register(user_id, str(user_id))
            services.save_gift(user_id, 'gift')
        token = services.preview(10, 'draw')
        services.draw(10, token)
        self.assertFalse(services.save_gift(1, 'changed'))
        reset_token = services.preview(10, 'new_game')
        backup = services.new_game(10, reset_token)
        self.assertTrue(backup.exists())
        self.assertEqual(services.status(), (0, 0, 0))
        self.assertEqual(services.register(3, 'new'), 'registered')
        import sqlite3
        with sqlite3.connect(backup) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(santa_for) FROM users').fetchone()[0], 2)

    def test_confirmation_expires_when_roster_changes(self):
        services.register(1, 'one')
        services.register(2, 'two')
        services.save_gift(1, 'gift')
        services.save_gift(2, 'gift')
        token = services.preview(10, 'draw')
        services.register(3, 'three')
        self.assertEqual(services.draw(10, token), [])
        self.assertEqual(services.status()[2], 0)

    def test_notification_retry_only_targets_pending_users(self):
        for user_id in (1, 2):
            services.register(user_id, str(user_id))
            services.save_gift(user_id, 'gift')
        token = services.preview(10, 'draw')
        services.draw(10, token)
        self.assertEqual(set(services.assigned_ids()), {1, 2})
        services.mark_notified(1)
        self.assertEqual(services.assigned_ids(), [2])
