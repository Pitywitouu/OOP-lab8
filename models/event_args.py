from datetime import datetime
from .enums import DeviceStatus, AlertSeverity


class EventArgs:
    pass


class DeviceStatusChangedEventArgs(EventArgs):
    def __init__(
        self,
        device_id: str,
        old_status: DeviceStatus,
        new_status: DeviceStatus,
        changed_at: datetime | None = None,
    ) -> None:
        self._device_id = device_id
        self._old_status = old_status
        self._new_status = new_status
        self._changed_at = changed_at if changed_at is not None else datetime.now()

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def DeviceId(self) -> str:
        return self._device_id

    @property
    def old_status(self) -> DeviceStatus:
        return self._old_status

    @property
    def OldStatus(self) -> DeviceStatus:
        return self._old_status

    @property
    def new_status(self) -> DeviceStatus:
        return self._new_status

    @property
    def NewStatus(self) -> DeviceStatus:
        return self._new_status

    @property
    def changed_at(self) -> datetime:
        return self._changed_at

    @property
    def ChangedAt(self) -> datetime:
        return self._changed_at

    def __repr__(self) -> str:
        return (
            f"DeviceStatusChangedEventArgs(device_id='{self._device_id}', "
            f"old_status={self._old_status}, new_status={self._new_status}, "
            f"changed_at={self._changed_at.isoformat()})"
        )


class DeviceAlertEventArgs(EventArgs):
    def __init__(
        self,
        device_id: str,
        message: str,
        severity: AlertSeverity,
        occurred_at: datetime | None = None,
    ) -> None:
        self._device_id = device_id
        self._message = message
        self._severity = severity
        self._occurred_at = occurred_at if occurred_at is not None else datetime.now()

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def DeviceId(self) -> str:
        return self._device_id

    @property
    def message(self) -> str:
        return self._message

    @property
    def Message(self) -> str:
        return self._message

    @property
    def severity(self) -> AlertSeverity:
        return self._severity

    @property
    def Severity(self) -> AlertSeverity:
        return self._severity

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at

    @property
    def OccurredAt(self) -> datetime:
        return self._occurred_at

    def __repr__(self) -> str:
        return (
            f"DeviceAlertEventArgs(device_id='{self._device_id}', "
            f"severity={self._severity}, message='{self._message}', "
            f"occurred_at={self._occurred_at.isoformat()})"
        )
