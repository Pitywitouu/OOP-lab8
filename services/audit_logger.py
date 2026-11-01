from typing import Any
from models.event_args import DeviceStatusChangedEventArgs

class DeviceAuditLogger:
    def __init__(self) -> None:
        self._entries: list[str] = []

    @property
    def entries(self) -> tuple[str, ...]:
        return tuple(self._entries)

    @property
    def Entries(self) -> tuple[str, ...]:
        return tuple(self._entries)

    def handle_status_changed(self, sender: Any, e: DeviceStatusChangedEventArgs) -> None:
        entry = f"{e.changed_at}: {e.device_id}, {e.old_status} -> {e.new_status}"
        self._entries.append(entry)

    HandleStatusChanged = handle_status_changed

    def clear(self) -> None:
        self._entries.clear()
