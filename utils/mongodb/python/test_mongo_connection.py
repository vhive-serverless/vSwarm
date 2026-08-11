# MIT License
#
# Copyright (c) 2026 EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

from mongo_connection import MongoConnectionManager


class FakeAdmin:
    def __init__(self, client):
        self.client = client

    def command(self, command):
        self.client.commands.append(command)


class FakeClient:
    def __init__(self, uri, **options):
        self.uri = uri
        self.options = options
        self.commands = []
        self.closed = False
        self.admin = FakeAdmin(self)

    def __getitem__(self, database_name):
        return database_name

    def close(self):
        self.closed = True


class ClientFactory:
    def __init__(self):
        self.clients = []

    def __call__(self, uri, **options):
        client = FakeClient(uri, **options)
        self.clients.append(client)
        return client


class MongoConnectionManagerTest(unittest.TestCase):
    def test_per_invocation_creates_pings_and_closes_each_client(self):
        factory = ClientFactory()
        manager = MongoConnectionManager(
            "mongodb://backend:27017",
            "image_db",
            client_factory=factory,
        )

        for _ in range(2):
            with manager.database() as (database, setup_us):
                self.assertEqual(database, "image_db")
                self.assertGreaterEqual(setup_us, 0)

        self.assertEqual(len(factory.clients), 2)
        self.assertEqual(
            [client.commands for client in factory.clients],
            [["ping"], ["ping"]],
        )
        self.assertTrue(all(client.closed for client in factory.clients))

    def test_persistent_mode_reuses_client_until_manager_close(self):
        factory = ClientFactory()
        manager = MongoConnectionManager(
            "mongodb://backend:27017",
            "image_db",
            mode="persistent",
            client_factory=factory,
        )

        with manager.database():
            pass
        with manager.database():
            pass

        self.assertEqual(len(factory.clients), 1)
        self.assertFalse(factory.clients[0].closed)
        manager.close()
        self.assertTrue(factory.clients[0].closed)

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            MongoConnectionManager("mongodb://backend:27017", "image_db", mode="unknown")
        with self.assertRaises(ValueError):
            MongoConnectionManager("mongodb://backend:27017", "image_db", timeout_ms=0)


if __name__ == "__main__":
    unittest.main()
