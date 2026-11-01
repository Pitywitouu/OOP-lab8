import sys
from typing import Any
from models.event_args import DeviceAlertEventArgs

class ConsoleNotificationService:
    def __init__(self) -> None:
        self._notifications: list[str] = []

    @property
    def notifications(self) -> list[str]:
        return list(self._notifications)

    def handle_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        msg = f"[{e.severity}] {e.device_id}: {e.message}"
        self._notifications.append(msg)
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", errors="replace").decode("ascii"))

    HandleAlert = handle_alert
