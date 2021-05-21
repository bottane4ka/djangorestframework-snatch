import typing as t
from time import sleep
from django.test import TestCase
from rest.manager.models import NotifyCountModel

# Create your tests here.


class NotifyCountTestCase(TestCase):

    def setUp(self) -> t.NoReturn:
        data = {
            "table_schema": "test",
            "table_name": "test",
            "wait_time": 10,
            "max_count": 2,
            "last_update_datetime": None
        }
        NotifyCountModel.objects.create(**data)

    def test_update_count_lt_max_count(self):
        notify_count = NotifyCountModel.objects.get(table_schema="test", table_name="test")
        notify_count.count += 1
        notify_count.save()

        self.assertEqual(notify_count.count, 1)
        self.assertNotEqual(notify_count.last_update_datetime, None)

    def test_update_count_gt_max_count(self):
        notify_count = NotifyCountModel.objects.get(table_schema="test", table_name="test")
        notify_count.count += 2
        notify_count.save()

        self.assertEqual(notify_count.count, 0)
        self.assertEqual(notify_count.last_update_datetime, None)

    def test_update_count_gt_wait_time(self):
        notify_count = NotifyCountModel.objects.get(table_schema="test", table_name="test")
        notify_count.count += 1
        notify_count.save()
        sleep(notify_count.wait_time + 1)

        self.assertEqual(notify_count.count, 0)
        self.assertEqual(notify_count.last_update_datetime, None)
