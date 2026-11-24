"""Smoke tests for the local-only AADi Infinity Labs prototype."""
import os
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

class WebSmokeTest(unittest.TestCase):
    def test_home_and_admin(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        env = {**os.environ, "AADI_ADMIN_PASSWORD": "test-password-long-enough", "PORT": str(port)}
        proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(50):
                if proc.poll() is not None:
                    self.fail("Website exited before starting")
                try:
                    with urlopen(base + "/", timeout=1) as response:
                        page = response.read().decode("utf-8")
                        self.assertEqual(response.status, 200)
                        self.assertIn("AADi INFINITY", page)
                        self.assertIn("Indian Roots. Infinite Vision.", page)
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                self.fail("Website did not start")
            with urlopen(base + "/admin", timeout=2) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("Administrator sign in", response.read().decode())
            with urlopen(base + "/apps", timeout=2) as response:
                self.assertEqual(response.status, 200)
                self.assertNotIn('href="/app/storynest"', response.read().decode())
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)

if __name__ == "__main__":
    unittest.main()
