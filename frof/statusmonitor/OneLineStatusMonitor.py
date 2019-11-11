from datetime import datetime

from .StatusMonitor import StatusMonitor


class OneLineStatusMonitor(StatusMonitor):
    """
    A status monitor that keeps itself constrainted to a single line.

    Good for running in a CLI.
    During a run, prints:

        🤔 7 jobs running, 9 remaining.

    While the run boots, prints:

        Starting job with 17 jobs total.

    When a run has no more remaining jobs, prints:

        👌 0 jobs running, 0 remaining.

    """

    def __init__(self, fe: "FrofExecutor") -> None:
        """
        Create a new OneLineStatusMonitor.



        Arguments:
            fe (FrofExecutor): The Executor to print for during runs

        Returns:
            None

        """
        self.fe = fe
        self.started_time = datetime.now()
        self.total_job_count = len(self.fe.fp.as_networkx())

    def emit_status(self):
        """
        Emit the current status of self.fe.

        Prints directly to stdout. Uses emojis. This is not the most backward-
        compatible of all systems.

        Arguments:
            None

        Returns:
            None

        """
        next_job_count = len(self.fe.get_next_jobs())
        if next_job_count:
            emoji = "🤔"
        else:
            emoji = "👌"
        remaining = len(self.fe.get_current_network())

        pct = (self.total_job_count - remaining) / self.total_job_count
        print(
            f"{emoji} ———— {next_job_count} jobs running, {remaining} remaining ({int(100*pct)}%).         ",
            end="\r",
        )

    def launch_status(self):
        """
        Print the current status pre-run of the Plan.

        Arguments:
            None

        Returns:
            None

        """
        print(
            f"Starting job with {len(self.fe.get_network())} jobs total.         ",
            end="\r",
        )

