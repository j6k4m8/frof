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

    def __repr__(self) -> str:
        return f"<{self.cmd[:10]}>"


class NullJob(Job):
    """
    A no-op Job class that doesn't do anything.

    You can optionally add a delay, which is helpful for testing.
    """

    def __init__(self, delay: float = 0) -> None:
        """
        Create a new NullJob.

        Arguments:
            delay (float: 0): An optional delay when "run" is called. This lets
                you test out long-running things without actually hitting disk.

        Returns:
            None

        """
        self.delay = delay
        pass

    async def run(self, env_vars=None):
        process = await asyncio.create_subprocess_shell("#", env=env_vars)
        time.sleep(self.delay)
        _ = await process.communicate()

    def __str__(self) -> str:
        return "<NullJob>" if self.delay is 0 else "<NullJob delay={delay}s>"
