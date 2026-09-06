import subprocess
from dataclasses import dataclass

from courset.models import Check, CommandCheck, ManualCheck, MultipleCheck


@dataclass
class CheckResult:
    passed: bool
    detail: str


def run_check(check: Check) -> CheckResult:
    match check:
        case ManualCheck():
            return CheckResult(passed=True, detail="manual lesson")
        case CommandCheck():
            return _run_command_check(check)
        case MultipleCheck():
            for sub_check in check.checks:
                result = _run_command_check(sub_check)
                if not result.passed:
                    return result
            return CheckResult(passed=True, detail="all checks passed")


def _run_command_check(check: CommandCheck) -> CheckResult:
    try:
        process = subprocess.run(
            check.cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=check.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CheckResult(passed=False, detail=f"command timed out: {check.cmd}")

    output = "\n".join(
        part.strip() for part in (process.stdout, process.stderr) if part.strip()
    )
    if process.returncode != 0:
        return CheckResult(
            passed=False,
            detail=f"command failed (exit {process.returncode}): {output}",
        )
    if check.expect.strip() in output:
        return CheckResult(passed=True, detail=f"got: {output}")
    return CheckResult(
        passed=False,
        detail=f"expected '{check.expect}', got '{output}'",
    )
