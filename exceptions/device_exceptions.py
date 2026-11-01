class InvalidDeviceReadingException(Exception):
    def __init__(self, device_id: str, invalid_value: int, message: str | None = None) -> None:
        self.device_id = device_id
        self.invalid_value = invalid_value
        if message is None:
            message = (
                f"Giá trị chỉ số không hợp lệ {invalid_value} cho thiết bị '{device_id}'. "
                f"Chỉ số phải nằm trong khoảng từ 0 đến 100."
            )
        super().__init__(message)
