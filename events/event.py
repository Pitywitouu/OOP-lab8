from typing import Any, Callable


class Event:
    def __init__(self) -> None:
        self._handlers: list[Callable[[Any, Any], None]] = []

    def __iadd__(self, handler: Callable[[Any, Any], None]) -> "Event":
        # Đăng ký handler. Tránh đăng ký trùng cùng một handler nhiều lần
        if callable(handler) and handler not in self._handlers:
            self._handlers.append(handler)
        return self

    def __isub__(self, handler: Callable[[Any, Any], None]) -> "Event":
        # Hủy đăng ký handle
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self

    def add_handler(self, handler: Callable[[Any, Any], None]) -> None:
        # Phương thức hỗ trợ đăng ký handler
        self.__iadd__(handler)

    def remove_handler(self, handler: Callable[[Any, Any], None]) -> None:
        # Phương thức hỗ trợ hủy đăng ký handler
        self.__isub__(handler)

    def invoke(self, sender: Any, e: Any) -> None:
        # Phát sinh sự kiện tới tất cả các subscriber đã đăng ký
        for handler in list(self._handlers):
            handler(sender, e)

    def __call__(self, sender: Any, e: Any) -> None:
        self.invoke(sender, e)

    @property
    def handlers(self) -> tuple[Callable[[Any, Any], None], ...]:
        # Danh sách read-only các handler đã đăng ký
        return tuple(self._handlers)

    def clear(self) -> None:
        # Xóa tất cả các handler
        self._handlers.clear()

    def __len__(self) -> int:
        return len(self._handlers)

    def __repr__(self) -> str:
        return f"<Event handlers_count={len(self._handlers)}>"
