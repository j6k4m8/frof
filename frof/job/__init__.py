import asyncio


class Job:
    ...


class BashJob(Job):
    def __init__(self, cmd: str, use_env_vars=True, env=None) -> None:
        self.cmd = cmd
        self.use_env_vars = use_env_vars
        self.env = env if env else {}

    async def run(self, env_vars=None):
        cmd = self.cmd
        env = {}
        if self.use_env_vars:
            env = {**env_vars, **self.env}

        process = await asyncio.create_subprocess_shell(cmd, env=env)
        _ = await process.communicate()

    def __str__(self) -> str:
        return f"<{self.cmd[:10]}>"
