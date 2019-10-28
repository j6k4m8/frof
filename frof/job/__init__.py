import subprocess


class Job:
    ...


class BashJob(Job):
    def __init__(self, cmd: str) -> None:
        self.cmd = cmd.split()

    def run(self) -> bool:
        subprocess.check_output(self.cmd)
        return True

    def __str__(self) -> str:
        return f"<{self.cmd[:10]}>"
