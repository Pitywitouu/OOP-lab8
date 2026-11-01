"""Dịch vụ hiển thị thông báo thiết bị ra Console."""

import sys
from typing import Any
from models.event_args import DeviceAlertEventArgs

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ConsoleNotificationService:
    """
    Subscriber xử lý hiển thị cảnh báo thiết bị.
    
    Quy tắc:
    - Khi nhận sự kiện AlertRaised, in ra console định dạng:
      [{Severity}] {DeviceId}: {Message}
    """

    def __init__(self) -> None:
        self._notifications: list[str] = []

    @property
    def notifications(self) -> list[str]:
        """Danh sách các thông báo đã nhận (hữu ích cho kiểm thử)."""
        return list(self._notifications)

    def handle_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        """Handler nhận sự kiện cảnh báo từ thiết bị."""
        msg = f"[{e.severity}] {e.device_id}: {e.message}"
        self._notifications.append(msg)
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", errors="replace").decode("ascii"))

    HandleAlert = handle_alert
