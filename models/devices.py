from abc import ABC
from datetime import datetime
from events.event import Event
from exceptions.device_exceptions import InvalidDeviceReadingException
from .enums import DeviceStatus, AlertSeverity
from .event_args import DeviceStatusChangedEventArgs, DeviceAlertEventArgs


class TeachingDevice(ABC):
    def __init__(self, id: str, name: str) -> None:
        self._id: str = id
        self._name: str = name
        self._status: DeviceStatus = DeviceStatus.Available
        self.status_changed: Event = Event()
        self.alert_raised: Event = Event()

    @property
    def id(self) -> str:
        return self._id

    @property
    def Id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def Name(self) -> str:
        return self._name

    @property
    def status(self) -> DeviceStatus:
        return self._status

    @property
    def Status(self) -> DeviceStatus:
        return self._status

    @property
    def StatusChanged(self) -> Event:
        return self.status_changed

    @property
    def AlertRaised(self) -> Event:
        return self.alert_raised

    def change_status(self, new_status: DeviceStatus) -> None:
        if new_status == self._status:
            return

        old_status = self._status
        self._status = new_status
        args = DeviceStatusChangedEventArgs(
            device_id=self._id,
            old_status=old_status,
            new_status=new_status,
            changed_at=datetime.now(),
        )
        self._on_status_changed(args)

    ChangeStatus = change_status

    def _raise_alert(self, message: str, severity: AlertSeverity) -> None:  
        args = DeviceAlertEventArgs(
            device_id=self._id,
            message=message,
            severity=severity,
            occurred_at=datetime.now(),
        )
        self._on_alert_raised(args)

    raise_alert = _raise_alert
    RaiseAlert = _raise_alert

    def _on_status_changed(self, e: DeviceStatusChangedEventArgs) -> None:
        self.status_changed.invoke(self, e)

    on_status_changed = _on_status_changed
    OnStatusChanged = _on_status_changed

    def _on_alert_raised(self, e: DeviceAlertEventArgs) -> None:
        self.alert_raised.invoke(self, e)

    on_alert_raised = _on_alert_raised
    OnAlertRaised = _on_alert_raised

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self._id}', name='{self._name}', status={self._status}>"


class ProjectorRemote(TeachingDevice):
    def __init__(self, id: str, name: str, battery_level: int = 100) -> None:
        super().__init__(id, name)
        self._validate_battery(battery_level)
        self._battery_level: int = battery_level

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @property
    def BatteryLevel(self) -> int:
        return self._battery_level

    def _validate_battery(self, level: int) -> None:
        if not (0 <= level <= 100):
            raise InvalidDeviceReadingException(self.id, level)

    def update_battery_level(self, new_level: int) -> None:
        self._validate_battery(new_level)

        old_level = self._battery_level
        self._battery_level = new_level

        if new_level == 0:
            self._raise_alert(
                f"Điều khiển máy chiếu '{self.name}' ({self.id}) đã hết pin (0%)!",
                AlertSeverity.Critical,
            )
        elif new_level < 20:
            self._raise_alert(
                f"Điều khiển máy chiếu '{self.name}' ({self.id}) mức pin thấp: {new_level}%!",
                AlertSeverity.Warning,
            )
        else:
            pass

    UpdateBatteryLevel = update_battery_level


class AirConditionerRemote(TeachingDevice):
    def __init__(
        self,
        id: str,
        name: str,
        assigned_room: str,
        is_responsive: bool = True,
    ) -> None:
        super().__init__(id, name)
        self._assigned_room: str = assigned_room
        self._is_responsive: bool = is_responsive

    @property
    def assigned_room(self) -> str:
        return self._assigned_room

    @property
    def AssignedRoom(self) -> str:
        return self._assigned_room

    @property
    def is_responsive(self) -> bool:
        return self._is_responsive

    @property
    def IsResponsive(self) -> bool:
        return self._is_responsive

    def update_response_state(self, is_responsive: bool) -> None:
        old_state = self._is_responsive
        self._is_responsive = is_responsive

        if old_state is True and is_responsive is False:
            self._raise_alert(
                f"Điều khiển điều hòa '{self.name}' tại phòng {self._assigned_room} ({self.id}) không phản hồi!",
                AlertSeverity.Critical,
            )

    UpdateResponseState = update_response_state


class WirelessMicrophone(TeachingDevice):
    def __init__(
        self,
        id: str,
        name: str,
        battery_level: int = 100,
        signal_quality: int = 100,
    ) -> None:
        super().__init__(id, name)
        self._validate_reading(battery_level, "pin")
        self._validate_reading(signal_quality, "tín hiệu")
        self._battery_level: int = battery_level
        self._signal_quality: int = signal_quality

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @property
    def BatteryLevel(self) -> int:
        return self._battery_level

    @property
    def signal_quality(self) -> int:
        return self._signal_quality

    @property
    def SignalQuality(self) -> int:
        return self._signal_quality

    def _validate_reading(self, val: int, label: str) -> None:
        if not (0 <= val <= 100):
            raise InvalidDeviceReadingException(self.id, val)

    def update_battery_level(self, new_level: int) -> None:
        self._validate_reading(new_level, "pin")
        self._battery_level = new_level

        if new_level == 0:
            self._raise_alert(
                f"Micro không dây '{self.name}' ({self.id}) đã hết pin (0%)!",
                AlertSeverity.Critical,
            )
        elif new_level < 30:
            self._raise_alert(
                f"Micro không dây '{self.name}' ({self.id}) mức pin yếu: {new_level}%!",
                AlertSeverity.Warning,
            )

    UpdateBatteryLevel = update_battery_level

    def update_signal_quality(self, new_quality: int) -> None:
        self._validate_reading(new_quality, "tín hiệu")
        self._signal_quality = new_quality

        if new_quality == 0:
            self._raise_alert(
                f"Micro không dây '{self.name}' ({self.id}) mất tín hiệu hoàn toàn (0%)!",
                AlertSeverity.Critical,
            )
        elif new_quality < 40:
            self._raise_alert(
                f"Micro không dây '{self.name}' ({self.id}) chất lượng tín hiệu kém: {new_quality}%!",
                AlertSeverity.Warning,
            )

    UpdateSignalQuality = update_signal_quality
