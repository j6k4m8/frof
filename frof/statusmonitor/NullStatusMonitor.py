from .StatusMonitor import StatusMonitor


class NullStatusMonitor(StatusMonitor):
    """
    Abstract class for status-monitoring capabilities.

    Do not use directly.
    """

    def __init__(self, fe, **kwargs):
        return

    def launch_status(self):
        return

    def emit_status(self):
        return

