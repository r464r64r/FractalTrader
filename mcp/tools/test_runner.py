"""
Test Runner Tool for MCP Server.

Executes pytest tests and returns formatted results.
"""

import subprocess
from typing import Any

from mcp.config import DEFAULT_TEST_PATH, USE_DOCKER, DOCKER_CONTAINER_NAME


def run_tests(test_path: str = DEFAULT_TEST_PATH) -> dict[str, Any]:
    """
    Run pytest tests and return results.

    Args:
        test_path: Path to tests (default: "tests/")

    Returns:
        Dictionary containing:
            - passed: bool - Whether all tests passed
            - total: int - Total number of tests run
            - failed: int - Number of failed tests
            - output: str - Full pytest output
    """
    try:
        if USE_DOCKER:
            cmd = [
                "docker", "exec", DOCKER_CONTAINER_NAME,
                "python", "-m", "pytest", test_path,
                "-v", "--tb=short", "--color=no"
            ]
        else:
            cmd = [
                "python", "-m", "pytest", test_path,
                "-v", "--tb=short", "--color=no"
            ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Parse pytest output for summary
        passed_count = 0
        failed_count = 0

        for line in output.split("\n"):
            if " passed" in line:
                # Parse line like "37 passed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        try:
                            passed_count = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    if part == "failed" and i > 0:
                        try:
                            failed_count = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

        total_count = passed_count + failed_count
        all_passed = result.returncode == 0

        return {
            "passed": all_passed,
            "total": total_count,
            "failed": failed_count,
            "output": output
        }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "total": 0,
            "failed": 0,
            "output": "Error: Test execution timed out after 120 seconds"
        }
    except Exception as e:
        return {
            "passed": False,
            "total": 0,
            "failed": 0,
            "output": f"Error running tests: {str(e)}"
        }


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_run_tests_success
# [ ] test_run_tests_with_failures
# [ ] test_run_tests_timeout
# [ ] test_run_tests_invalid_path
# =============================================================================
