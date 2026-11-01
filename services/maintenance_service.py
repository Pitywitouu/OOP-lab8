from typing import Any
from models.enums import AlertSeverity
from models.event_args import DeviceAlertEventArgs

class MaintenanceService:
    def __init__(self) -> None:
        self._requests: list[str] = []

    @property
    def requests(self) -> tuple[str, ...]:
        return tuple(self._requests)

    @property
    def Requests(self) -> tuple[str, ...]:
        return tuple(self._requests)

    def handle_critical_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        if e.severity != AlertSeverity.Critical:
            return

        req = f"Maintenance request for {e.device_id}: {e.message}"
        self._requests.append(req)

    HandleCriticalAlert = handle_critical_alert

    def clear(self) -> None:
        self._requests.clear()
