import time
import subprocess


class Job:
    ...


class BashJob(Job):
    """
    BashJobs manage the execution of simple commands in a local shell.

    These are executed in the current working directory.
    """

    def __init__(self, cmd: str, use_env_vars=True, env=None) -> None:
        """
        Create a new BashJob.

        Arguments:
            cmd (str): The command to execute
            use_env_vars (bool: True): Whether to set environment variables
            env (dict: None): Custom environment variables to use

        Returns:
            None

        """
        self.cmd = cmd
        self.use_env_vars = use_env_vars
        self.env = env if env else {}

    def run(self, env_vars=None):
        """
        Run the command.

        Arguments:
            env_vars (dict: None): Custom environment variables to use

        Returns:
            None

        """
        cmd = self.cmd
        env = {}
        if self.use_env_vars:
            env = {**env_vars, **self.env}

        # Cast all env-vars to string (int/float other types are not supported
        # by Python's subprocess module).
        env = {k: str(v) for k, v in env.items()}
        subprocess.check_output(cmd, shell=True, env=env)

    def __str__(self) -> str:
        """
        Produce this BashJob as a string.

        Returns:
            str: A human-readable string

        """
        return f"<{self.cmd[:10]}>"

    def __repr__(self) -> str:
        """
        Produce this BashJob as a string.

        Returns:
            str: A human-readable string

        """
        return f"BashJob('{self.cmd}', env={self.env})"


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

    def run(self, env_vars=None):
        time.sleep(self.delay)

    def __str__(self) -> str:
        return "<NullJob>" if self.delay is 0 else "<NullJob delay={delay}s>"
