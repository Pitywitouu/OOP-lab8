from enum import Enum

class DeviceStatus(str, Enum):
    Available = "Available"
    Borrowed = "Borrowed"
    UnderMaintenance = "UnderMaintenance"

    def __str__(self) -> str:
        return self.value

class AlertSeverity(str, Enum):
    Information = "Information"
    Warning = "Warning"
    Critical = "Critical"

    def __str__(self) -> str:
        return self.value
