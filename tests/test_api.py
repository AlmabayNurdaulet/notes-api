"""HTTP contract tests using only the Python standard library."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


class NotesAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a separate port so the tests do not hit an already-running app.
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        cls.base_url = f"http://127.0.0.1:{port}"
        cls.log = tempfile.TemporaryFile(mode="w+t")
        cls.addClassCleanup(cls.log.close)
        cls.server = subprocess.Popen(
            ["./scripts/run.sh"],
            cwd=ROOT,
            env={**os.environ, "PORT": str(port)},
            stdout=cls.log,
            stderr=cls.log,
        )
        cls.addClassCleanup(cls.stop_server)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if cls.server.poll() is not None:
                cls.log.seek(0)
                raise RuntimeError(f"Server stopped during startup:\n{cls.log.read()}")
            try:
                status, _ = cls.request("/")
                if status == 200:
                    return
            except (URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(0.05)
        raise RuntimeError("Server did not become ready within 10 seconds")

    @classmethod
    def stop_server(cls):
        if cls.server.poll() is None:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait(timeout=3)

    @classmethod
    def request(cls, path, method="GET", body=None):
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = Request(cls.base_url + path, data=body, headers=headers, method=method)
        try:
            with urlopen(req, timeout=2) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as response:
            try:
                return response.code, response.read().decode("utf-8")
            finally:
                response.close()

    def create_note(self, text):
        status, body = self.request(
            "/notes", "POST", json.dumps({"text": text}).encode("utf-8")
        )
        self.assertEqual(status, 201)
        return json.loads(body)

    def test_healthz_is_fast_and_repeatable(self):
        for _ in range(2):
            started = time.monotonic()
            status, body = self.request("/healthz")
            self.assertEqual(status, 200)
            self.assertEqual(body, "OK")
            self.assertLess(time.monotonic() - started, 1)

    def test_root_lists_notes(self):
        status, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIsInstance(json.loads(body)["notes"], list)

    def test_create_note(self):
        note = self.create_note("A new note")
        self.assertEqual(note["text"], "A new note")
        self.assertTrue(note["id"])

    def test_get_created_note(self):
        note = self.create_note("Find this note")
        status, body = self.request(f"/notes/{note['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), note)

    def test_missing_note(self):
        status, body = self.request("/notes/not-an-id")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)["error"], "not found")

    def test_unknown_route(self):
        status, body = self.request("/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)["error"], "not found")

    def test_invalid_json(self):
        status, body = self.request("/notes", "POST", b"{not-json}")
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"], "invalid json")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NotesAPITests)
    total = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    passed = max(0, result.testsRun - len(result.failures) - len(result.errors)
                 - len(result.skipped) - len(result.expectedFailures)
                 - len(result.unexpectedSuccesses))
    print(f"TESTS: {passed}/{total}", flush=True)
    sys.exit(0 if result.wasSuccessful() and passed == total else 1)
