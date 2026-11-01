from typing import Iterable, Any
from models.devices import TeachingDevice
from services.notification_service import ConsoleNotificationService
from services.audit_logger import DeviceAuditLogger
from services.maintenance_service import MaintenanceService

class DeviceMonitoringCoordinator:
    def __init__(
        self,
        devices: Iterable[TeachingDevice],
        notification_service: ConsoleNotificationService,
        audit_logger: DeviceAuditLogger,
        maintenance_service: MaintenanceService,
    ) -> None:
        self._devices: list[TeachingDevice] = list(devices)
        self._notification_service: ConsoleNotificationService = notification_service
        self._audit_logger: DeviceAuditLogger = audit_logger
        self._maintenance_service: MaintenanceService = maintenance_service
        self._is_subscribed: bool = False

    @property
    def devices(self) -> list[TeachingDevice]:
        return list(self._devices)

    @property
    def is_subscribed(self) -> bool:
        return self._is_subscribed

    def subscribe(self) -> None:
        if self._is_subscribed:
            return

        for device in self._devices:
            device.status_changed += self._audit_logger.handle_status_changed
            device.alert_raised += self._notification_service.handle_alert
            device.alert_raised += self._maintenance_service.handle_critical_alert

        self._is_subscribed = True

    Subscribe = subscribe

    def unsubscribe(self) -> None:
        # Hủy đúng các đăng ký đã tạo cho toàn bộ thiết bị
        if not self._is_subscribed:
            return

        for device in self._devices:
            device.status_changed -= self._audit_logger.handle_status_changed
            device.alert_raised -= self._notification_service.handle_alert
            device.alert_raised -= self._maintenance_service.handle_critical_alert

        self._is_subscribed = False

    Unsubscribe = unsubscribe

    def dispose(self) -> None:
        # Thực hiện dọn dẹp bằng cách hủy đăng ký tất cả các handler
        self.unsubscribe()

    Dispose = dispose

    def add_device(self, device: TeachingDevice) -> None:
        # Thêm thiết bị mới vào danh sách theo dõi
        if device not in self._devices:
            self._devices.append(device)
            if self._is_subscribed:
                device.status_changed += self._audit_logger.handle_status_changed
                device.alert_raised += self._notification_service.handle_alert
                device.alert_raised += self._maintenance_service.handle_critical_alert

    def remove_device(self, device: TeachingDevice) -> None:
        # Xóa thiết bị khỏi danh sách theo dõi và hủy đăng ký event
        if device in self._devices:
            if self._is_subscribed:
                device.status_changed -= self._audit_logger.handle_status_changed
                device.alert_raised -= self._notification_service.handle_alert
                device.alert_raised -= self._maintenance_service.handle_critical_alert
            self._devices.remove(device)

    def __enter__(self) -> "DeviceMonitoringCoordinator":
        self.subscribe()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.dispose()
