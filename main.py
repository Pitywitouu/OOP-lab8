import sys
from models.enums import DeviceStatus, AlertSeverity
from models.devices import ProjectorRemote, AirConditionerRemote, WirelessMicrophone
from services.notification_service import ConsoleNotificationService
from services.audit_logger import DeviceAuditLogger
from services.maintenance_service import MaintenanceService
from services.filtered_subscriber import FilteredAlertSubscriber
from monitoring.coordinator import DeviceMonitoringCoordinator
from exceptions.device_exceptions import InvalidDeviceReadingException

def print_header(title: str) -> None:
    print(f"\n{'=' * 65}")
    print(f" {title.upper()}")
    print(f"{'=' * 65}")

def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass

    print_header("1. KHỞI TẠO CÁC THIẾT BỊ GIẢNG DẠY (PUBLISHERS)")
    projector = ProjectorRemote("PRJ-301", "Điều khiển Máy chiếu Epson", battery_level=100)
    ac = AirConditionerRemote("AC-301", "Điều khiển Điều hòa Daikin", assigned_room="Phòng 301", is_responsive=True)
    mic = WirelessMicrophone("MIC-301", "Micro Không dây Shure", battery_level=90, signal_quality=95)

    devices = [projector, ac, mic]
    for d in devices:
        print(f" [+] {d}")

    print_header("2. KHỞI TẠO CÁC DỊCH VỤ (SUBSCRIBERS)")
    notif_service = ConsoleNotificationService()
    audit_logger = DeviceAuditLogger()
    maint_service = MaintenanceService()

    critical_vip_sms: list[str] = []
    sms_subscriber = FilteredAlertSubscriber(
        filter=lambda alert: alert.severity == AlertSeverity.Critical,
        action=lambda alert: critical_vip_sms.append(
            f"[VIP SMS KHẨN CẤP] Thiết bị {alert.device_id}: {alert.message}"
        ),
    )

    print_header("3. ĐIỀU PHỐI ĐĂNG KÝ SỰ KIỆN (COORDINATOR)")
    coordinator = DeviceMonitoringCoordinator(
        devices=devices,
        notification_service=notif_service,
        audit_logger=audit_logger,
        maintenance_service=maint_service,
    )
    coordinator.subscribe()
    print(" -> Đã đăng ký tất cả các event handlers qua DeviceMonitoringCoordinator.")

    mic.alert_raised += sms_subscriber.handle_alert
    print(" -> Đã gắn thêm FilteredAlertSubscriber (VIP SMS) vào Micro.")

    print_header("4. MÔ PHỎNG HOẠT ĐỘNG VÀ PHÁT SINH SỰ KIỆN")

    print("\n--- a. Thay đổi trạng thái thiết bị ---")
    print("Giảng viên mượn máy chiếu và micro:")
    projector.change_status(DeviceStatus.Borrowed)
    mic.change_status(DeviceStatus.Borrowed)

    print("Cố gắng mượn lại máy chiếu (trùng trạng thái cũ -> không phát event):")
    projector.change_status(DeviceStatus.Borrowed)

    print("\n--- b. Cập nhật chỉ số máy chiếu ---")
    print("Pin giảm từ 100% xuống 75% (vùng an toàn >= 20% -> không cảnh báo):")
    projector.update_battery_level(75)

    print("Pin giảm xuống 15% (< 20% -> phát cảnh báo Warning):")
    projector.update_battery_level(15)

    print("Pin cạn về 0% (= 0% -> phát cảnh báo Critical -> tạo yêu cầu bảo trì):")
    projector.update_battery_level(0)

    print("\n--- c. Cập nhật trạng thái phản hồi điều hòa ---")
    print("Điều hòa gặp sự cố mất tín hiệu (True -> False -> phát Critical):")
    ac.update_response_state(False)

    print("Điều hòa tiếp tục không phản hồi (False -> False -> không phát lặp lại):")
    ac.update_response_state(False)

    print("\n--- d. Cập nhật pin và tín hiệu micro không dây ---")
    print("Micro pin giảm xuống 25% (< 30% -> Warning):")
    mic.update_battery_level(25)

    print("Tín hiệu micro giảm xuống 35% (< 40% -> Warning):")
    mic.update_signal_quality(35)

    print("Micro mất sóng hoàn toàn (Signal = 0% -> Critical -> SMS & Bảo trì):")
    mic.update_signal_quality(0)

    print("\n--- e. Kiểm tra ngoại lệ khi đọc giá trị bất thường (ngoài 0-100) ---")
    try:
        print("Cố tình gán mức pin micro = 125%:")
        mic.update_battery_level(125)
    except InvalidDeviceReadingException as ex:
        print(f" [BẮT NGOẠI LỆ THÀNH CÔNG] {ex}")

    print_header("5. KẾT QUẢ TỔNG HỢP TỪ CÁC SUBSCRIBERS")

    print("\n[A] NHẬT KÝ KIỂM TOÁN (DeviceAuditLogger - Lịch sử đổi trạng thái):")
    for idx, entry in enumerate(audit_logger.entries, 1):
        print(f"  {idx}. {entry}")

    print("\n[B] YÊU CẦU BẢO TRÌ (MaintenanceService - Chỉ nhận sự cố Critical):")
    for idx, req in enumerate(maint_service.requests, 1):
        print(f"  {idx}. {req}")

    print("\n[C] BỘ LỌC ĐẶC BIỆT (FilteredAlertSubscriber - Chỉ Critical SMS):")
    for idx, sms in enumerate(critical_vip_sms, 1):
        print(f"  {idx}. {sms}")

    print_header("6. HỦY ĐĂNG KÝ VÀ DỌN DẸP TÀI NGUYÊN (UNSUBSCRIBE / DISPOSE)")
    coordinator.unsubscribe()
    print(" -> Đã hủy đăng ký thành công qua coordinator.unsubscribe().")

    print("Thử thay đổi trạng thái sau khi unsubscribe (không được ghi thêm log):")
    count_before = len(audit_logger.entries)
    projector.change_status(DeviceStatus.Available)
    print(f"Số lượng log trước: {count_before}, sau: {len(audit_logger.entries)} (Chính xác!)")

    print("\nCHƯƠNG TRÌNH ĐÃ HOÀN THÀNH!")


if __name__ == "__main__":
    main()
