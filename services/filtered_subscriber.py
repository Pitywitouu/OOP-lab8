from typing import Any, Callable
from models.event_args import DeviceAlertEventArgs

AlertFilter = Callable[[DeviceAlertEventArgs], bool]
AlertAction = Callable[[DeviceAlertEventArgs], None]

class FilteredAlertSubscriber:
    def __init__(
        self,
        filter: AlertFilter,
        action: AlertAction,
    ) -> None:
        self._filter = filter
        self._action = action

    @property
    def filter(self) -> AlertFilter:
        return self._filter

    @property
    def action(self) -> AlertAction:
        return self._action

    def handle_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        if self._filter(e):
            self._action(e)

    HandleAlert = handle_alert
