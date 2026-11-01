import unittest
from datetime import datetime
from models.enums import DeviceStatus, AlertSeverity
from models.event_args import DeviceStatusChangedEventArgs, DeviceAlertEventArgs
from models.devices import (
    TeachingDevice,
    ProjectorRemote,
    AirConditionerRemote,
    WirelessMicrophone,
)
from exceptions.device_exceptions import InvalidDeviceReadingException
from services.notification_service import ConsoleNotificationService
from services.audit_logger import DeviceAuditLogger
from services.maintenance_service import MaintenanceService
from services.filtered_subscriber import FilteredAlertSubscriber
from monitoring.coordinator import DeviceMonitoringCoordinator

class TestTeachingDeviceAndEvents(unittest.TestCase):
    def test_initial_status(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        self.assertEqual(p.status, DeviceStatus.Available)
        self.assertEqual(p.id, "PRJ-01")
        self.assertEqual(p.name, "Máy chiếu Sony")

    def test_change_status_fires_event(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        events: list[DeviceStatusChangedEventArgs] = []
        p.status_changed += lambda sender, e: events.append(e)

        p.change_status(DeviceStatus.Borrowed)

        self.assertEqual(p.status, DeviceStatus.Borrowed)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].device_id, "PRJ-01")
        self.assertEqual(events[0].old_status, DeviceStatus.Available)
        self.assertEqual(events[0].new_status, DeviceStatus.Borrowed)
        self.assertIsInstance(events[0].changed_at, datetime)

    def test_change_status_duplicate_does_not_fire_event(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        events: list[DeviceStatusChangedEventArgs] = []
        p.status_changed += lambda sender, e: events.append(e)

        p.change_status(DeviceStatus.Available)  # Trạng thái ban đầu đã là Available
        self.assertEqual(len(events), 0)

        p.change_status(DeviceStatus.UnderMaintenance)
        self.assertEqual(len(events), 1)

        p.change_status(DeviceStatus.UnderMaintenance)  # Trùng trạng thái vừa đổi
        self.assertEqual(len(events), 1)

class TestProjectorRemote(unittest.TestCase):
    def test_battery_safe_zone_no_alert(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony", 100)
        alerts: list[DeviceAlertEventArgs] = []
        p.alert_raised += lambda sender, e: alerts.append(e)

        p.update_battery_level(85)
        p.update_battery_level(20)

        self.assertEqual(len(alerts), 0)

    def test_battery_below_20_warning(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony", 100)
        alerts: list[DeviceAlertEventArgs] = []
        p.alert_raised += lambda sender, e: alerts.append(e)

        p.update_battery_level(15)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.Warning)
        self.assertIn("15%", alerts[0].message)

    def test_battery_zero_critical(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony", 100)
        alerts: list[DeviceAlertEventArgs] = []
        p.alert_raised += lambda sender, e: alerts.append(e)

        p.update_battery_level(0)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.Critical)
        self.assertIn("0%", alerts[0].message)

    def test_invalid_battery_reading_raises_exception(self) -> None:
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony", 100)
        with self.assertRaises(InvalidDeviceReadingException):
            p.update_battery_level(-5)
        with self.assertRaises(InvalidDeviceReadingException):
            p.update_battery_level(105)


class TestAirConditionerRemote(unittest.TestCase):
    def test_unresponsive_fires_critical_alert(self) -> None:
        ac = AirConditionerRemote("AC-01", "Điều hòa Daikin", "P301", is_responsive=True)
        alerts: list[DeviceAlertEventArgs] = []
        ac.alert_raised += lambda sender, e: alerts.append(e)

        ac.update_response_state(False)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.Critical)
        self.assertIn("P301", alerts[0].message)

    def test_unresponsive_no_duplicate_alert(self) -> None:
        ac = AirConditionerRemote("AC-01", "Điều hòa Daikin", "P301", is_responsive=True)
        alerts: list[DeviceAlertEventArgs] = []
        ac.alert_raised += lambda sender, e: alerts.append(e)

        ac.update_response_state(False)
        ac.update_response_state(False) 

        self.assertEqual(len(alerts), 1)


class TestWirelessMicrophone(unittest.TestCase):
    def test_battery_warning_and_critical(self) -> None:
        mic = WirelessMicrophone("MIC-01", "Micro Shure", 100, 100)
        alerts: list[DeviceAlertEventArgs] = []
        mic.alert_raised += lambda sender, e: alerts.append(e)

        mic.update_battery_level(29)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.Warning)

        mic.update_battery_level(0)
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[1].severity, AlertSeverity.Critical)

    def test_signal_warning_and_critical(self) -> None:
        mic = WirelessMicrophone("MIC-01", "Micro Shure", 100, 100)
        alerts: list[DeviceAlertEventArgs] = []
        mic.alert_raised += lambda sender, e: alerts.append(e)

        mic.update_signal_quality(39)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.Warning)

        mic.update_signal_quality(0)
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[1].severity, AlertSeverity.Critical)

    def test_invalid_readings_raise_exception(self) -> None:
        mic = WirelessMicrophone("MIC-01", "Micro Shure", 100, 100)
        with self.assertRaises(InvalidDeviceReadingException):
            mic.update_battery_level(120)
        with self.assertRaises(InvalidDeviceReadingException):
            mic.update_signal_quality(-1)


class TestServices(unittest.TestCase):
    def test_console_notification_service(self) -> None:
        service = ConsoleNotificationService()
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        p.alert_raised += service.handle_alert

        p.update_battery_level(10)
        self.assertEqual(len(service.notifications), 1)
        self.assertIn("[Warning] PRJ-01:", service.notifications[0])

    def test_device_audit_logger(self) -> None:
        logger = DeviceAuditLogger()
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        p.status_changed += logger.handle_status_changed

        p.change_status(DeviceStatus.Borrowed)
        p.change_status(DeviceStatus.UnderMaintenance)

        self.assertEqual(len(logger.entries), 2)
        self.assertIn("PRJ-01, Available -> Borrowed", logger.entries[0])
        self.assertIn("PRJ-01, Borrowed -> UnderMaintenance", logger.entries[1])

    def test_maintenance_service_only_critical(self) -> None:
        maint = MaintenanceService()
        p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        p.alert_raised += maint.handle_critical_alert

        p.update_battery_level(15)  # Warning -> không tạo yêu cầu
        self.assertEqual(len(maint.requests), 0)

        p.update_battery_level(0)  # Critical -> tạo yêu cầu
        self.assertEqual(len(maint.requests), 1)
        self.assertIn("Maintenance request for PRJ-01", maint.requests[0])

    def test_filtered_alert_subscriber(self) -> None:
        captured: list[DeviceAlertEventArgs] = []
        subscriber = FilteredAlertSubscriber(
            filter=lambda e: e.severity == AlertSeverity.Critical,
            action=lambda e: captured.append(e),
        )

        mic = WirelessMicrophone("MIC-01", "Micro Shure")
        mic.alert_raised += subscriber.handle_alert

        mic.update_battery_level(25)  # Warning -> bị lọc
        self.assertEqual(len(captured), 0)

        mic.update_battery_level(0)  # Critical -> lọt qua bộ lọc
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0].severity, AlertSeverity.Critical)


class TestDeviceMonitoringCoordinator(unittest.TestCase):
    def setUp(self) -> None:
        self.p = ProjectorRemote("PRJ-01", "Máy chiếu Sony")
        self.ac = AirConditionerRemote("AC-01", "Điều hòa Daikin", "P101")
        self.mic = WirelessMicrophone("MIC-01", "Micro Shure")
        self.devices = [self.p, self.ac, self.mic]

        self.notif = ConsoleNotificationService()
        self.logger = DeviceAuditLogger()
        self.maint = MaintenanceService()

        self.coordinator = DeviceMonitoringCoordinator(
            self.devices,
            self.notif,
            self.logger,
            self.maint,
        )

    def test_subscribe_registers_all_handlers(self) -> None:
        self.coordinator.subscribe()
        self.assertTrue(self.coordinator.is_subscribed)

        self.coordinator.subscribe()
        self.assertEqual(len(self.p.status_changed), 1)
        self.assertEqual(len(self.p.alert_raised), 2)  # notif & maint

        # Kiểm tra sự kiện lan tỏa tới các subscriber
        self.p.change_status(DeviceStatus.Borrowed)
        self.assertEqual(len(self.logger.entries), 1)

        self.ac.update_response_state(False)
        self.assertEqual(len(self.maint.requests), 1)
        self.assertEqual(len(self.notif.notifications), 1)

    def test_unsubscribe_removes_handlers(self) -> None:
        self.coordinator.subscribe()
        self.coordinator.unsubscribe()
        self.assertFalse(self.coordinator.is_subscribed)

        self.p.change_status(DeviceStatus.Borrowed)
        self.ac.update_response_state(False)

        self.assertEqual(len(self.logger.entries), 0)
        self.assertEqual(len(self.maint.requests), 0)

    def test_context_manager_using_pattern(self) -> None:
        with DeviceMonitoringCoordinator(
            [self.p], self.notif, self.logger, self.maint
        ) as coord:
            self.assertTrue(coord.is_subscribed)
            self.p.change_status(DeviceStatus.Borrowed)
            self.assertEqual(len(self.logger.entries), 1)

        self.assertFalse(coord.is_subscribed)
        self.p.change_status(DeviceStatus.UnderMaintenance)
        self.assertEqual(len(self.logger.entries), 1)

if __name__ == "__main__":
    unittest.main()
