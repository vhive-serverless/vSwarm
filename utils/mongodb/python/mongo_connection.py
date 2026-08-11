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

"""MongoDB connection lifecycles for snapshot-restored functions."""

from contextlib import contextmanager
from time import perf_counter_ns

from pymongo import MongoClient


PER_INVOCATION = "per-invocation"
PERSISTENT = "persistent"
CONNECTION_MODES = (PER_INVOCATION, PERSISTENT)


class MongoConnectionManager:
    """Provide either request-scoped or process-scoped MongoDB clients.

    Request-scoped mode is the restore-safe default: it creates and verifies a
    fresh client after every function invocation begins and closes it before
    the invocation returns. Persistent mode exists to measure reconnection
    overhead against the historical vSwarm behavior.
    """

    def __init__(
        self,
        uri,
        database_name,
        mode=PER_INVOCATION,
        timeout_ms=2000,
        client_factory=MongoClient,
    ):
        if mode not in CONNECTION_MODES:
            raise ValueError(
                f"unsupported MongoDB connection mode {mode!r}; "
                f"expected one of {CONNECTION_MODES}"
            )
        if timeout_ms <= 0:
            raise ValueError("MongoDB timeout must be positive")

        self.uri = uri
        self.database_name = database_name
        self.mode = mode
        self.timeout_ms = timeout_ms
        self._client_factory = client_factory
        self._persistent_client = None
        if self.mode == PERSISTENT:
            self._persistent_client = self._new_client()

    def _new_client(self):
        return self._client_factory(
            self.uri,
            connectTimeoutMS=self.timeout_ms,
            serverSelectionTimeoutMS=self.timeout_ms,
            socketTimeoutMS=self.timeout_ms,
        )

    @contextmanager
    def database(self):
        """Yield ``(database, setup_microseconds)`` for one invocation."""

        request_scoped = self.mode == PER_INVOCATION
        started_ns = perf_counter_ns()
        client = self._new_client() if request_scoped else self._persistent_client
        try:
            if request_scoped:
                # MongoClient construction is lazy. Ping forces a new TCP
                # connection while it is safe to report setup time separately.
                client.admin.command("ping")
            setup_us = (perf_counter_ns() - started_ns) // 1000
            yield client[self.database_name], setup_us
        finally:
            if request_scoped:
                client.close()

    def close(self):
        """Close the historical process-scoped client, if configured."""

        if self._persistent_client is not None:
            self._persistent_client.close()
            self._persistent_client = None
