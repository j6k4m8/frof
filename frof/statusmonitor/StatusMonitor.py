import abc


class StatusMonitor(abc.ABC):
    """
    Abstract class for status-monitoring capabilities.

    Do not use directly.
    """

    ...

    def emit_status(self):
        """
        Emit a status for the contained FrofPlan.

        Arguments:
            None

        Returns:
            None

        """
        ...
