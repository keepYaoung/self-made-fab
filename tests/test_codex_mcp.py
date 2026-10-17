import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "codex_mcp.py"

BASE = """model = "x"

[features]
js_repl = false

[mcp_servers.keep]
command = "/bin/keep"
args = []

[mcp_servers.keep.env]
A = "1"
"""


class CodexMcpTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.config = Path(self.home.name) / "config.toml"
        self.config.write_text(BASE, encoding="utf-8")

    def tearDown(self):
        self.home.cleanup()

    def run_tool(self, *args, check=True):
        env = dict(os.environ, CODEX_HOME=self.home.name)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], env=env, capture_output=True, text=True, check=check
        )

    def servers(self):
        return tomllib.loads(self.config.read_text(encoding="utf-8"))["mcp_servers"]

    def test_add_then_remove_restores_file(self):
        self.run_tool("add", "probe", "--command", "/bin/uv", "--env", "K=v w", "--", "tool", "run", "x")
        self.run_tool("add", "web", "--url", "http://127.0.0.1:1/mcp")
        self.run_tool("remove", "probe")
        self.run_tool("remove", "web")
        self.assertEqual(self.config.read_text(encoding="utf-8"), BASE)

    def test_server_args_may_start_with_dashes(self):
        self.run_tool("add", "b", "--command", "/bin/uv", "--tool-timeout", "30", "--", "run", "--python", "3.12", "--frozen")
        server = self.servers()["b"]
        self.assertEqual(server["args"], ["run", "--python", "3.12", "--frozen"])
        self.assertEqual(server["tool_timeout_sec"], 30)

    def test_replace_keeps_other_servers(self):
        self.run_tool("add", "b", "--command", "/bin/one", "--env", "X=1")
        self.run_tool("add", "b", "--command", "/bin/two", "--disabled")
        servers = self.servers()
        self.assertEqual(servers["b"]["command"], "/bin/two")
        self.assertFalse(servers["b"]["enabled"])
        self.assertNotIn("env", servers["b"])
        self.assertEqual(servers["keep"]["env"], {"A": "1"})

    def test_backup_written(self):
        self.run_tool("add", "b", "--url", "http://x/")
        self.assertEqual(self.config.with_suffix(".toml.bak").read_text(encoding="utf-8"), BASE)

    def test_rejects_bad_name_and_both_targets(self):
        self.assertNotEqual(self.run_tool("add", "bad name", "--url", "http://x/", check=False).returncode, 0)
        result = self.run_tool("add", "b", "--url", "http://x/", "--command", "/bin/x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.config.read_text(encoding="utf-8"), BASE)


if __name__ == "__main__":
    unittest.main()

