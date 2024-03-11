class ProxyError(Exception):
    def __init__(self) -> None:
        super().__init__()
        self.message = "Proxy Error"


class VideoNotFoundError(Exception):
    def __init__(self, youtube_id: str) -> None:
        super().__init__()
        self.message = f"No Video Found {youtube_id}"
