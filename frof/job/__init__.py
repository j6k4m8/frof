import asyncio


class Job:
    ...


class BashJob(Job):
    def __init__(self, cmd: str) -> None:
        self.cmd = cmd

    async def run(self):
        process = await asyncio.create_subprocess_shell(self.cmd)
        _ = await process.communicate()

    def __str__(self) -> str:
        return f"<{self.cmd[:10]}>"
