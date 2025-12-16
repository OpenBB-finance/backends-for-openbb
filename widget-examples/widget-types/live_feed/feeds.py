import asyncio
import json
from dataclasses import dataclass, field
from typing import Callable, Literal
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

FeedKey = Literal["toa", "phx", "bwe"]


@dataclass
class NewsMessage:
    id: str
    title: str
    time: int
    source: FeedKey
    body: str | None = None
    url: str | None = None
    symbols: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "url": self.url,
            "symbols": self.symbols,
            "time": self.time,
            "source": self.source,
        }


@dataclass
class FeedConfig:
    key: FeedKey
    url: str
    heartbeat_interval: float


FEED_CONFIGS: dict[FeedKey, FeedConfig] = {
    "toa": FeedConfig(
        key="toa",
        url="wss://news.treeofalpha.com/ws",
        heartbeat_interval=10.0,
    ),
    "phx": FeedConfig(
        key="phx",
        url="wss://wss.phoenixnews.io",
        heartbeat_interval=10.0,
    ),
    "bwe": FeedConfig(
        key="bwe",
        url="ws://public.bwe-ws.com:8001",
        heartbeat_interval=60.0,
    ),
}


def parse_symbols(data: list | None) -> list[str]:
    if not data:
        return []
    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], str):
            return data
        if isinstance(data[0], dict) and "symbol" in data[0]:
            return [s["symbol"] for s in data]
    return []


def transform_toa(raw: dict) -> NewsMessage | None:
    if not raw.get("_id") and not raw.get("title") and not raw.get("body"):
        return None

    title = raw.get("title", "")
    body = raw.get("body")

    if body and not raw.get("source"):
        title = body
        body = None

    time_val = raw.get("time", int(datetime.now().timestamp() * 1000))
    url = raw.get("url") or raw.get("link")

    return NewsMessage(
        id=raw.get("_id", f"toa-{time_val}"),
        title=title,
        body=body,
        url=url,
        symbols=parse_symbols(raw.get("symbols")),
        time=time_val,
        source="toa",
    )


def transform_phx(raw: dict) -> NewsMessage | None:
    if not raw.get("_id") and not raw.get("title") and not raw.get("body"):
        return None

    title = raw.get("title", "")
    body = raw.get("body")

    if body and raw.get("name"):
        title = body
        body = None

    if raw.get("coin"):
        title = f"{raw['coin']}: {title}"
    elif raw.get("sourceName") and raw.get("source") == "Webs":
        title = f"{raw['sourceName']}: {title}"

    time_val = raw.get("time", int(datetime.now().timestamp() * 1000))
    url = raw.get("url") or raw.get("link")

    return NewsMessage(
        id=raw.get("_id", f"phx-{time_val}"),
        title=title,
        body=body,
        url=url,
        symbols=parse_symbols(raw.get("symbols")),
        time=time_val,
        source="phx",
    )


def transform_bwe(raw: dict) -> NewsMessage | None:
    if not raw.get("_id") and not raw.get("title") and not raw.get("body"):
        return None

    title = raw.get("title", "")
    body = raw.get("body")

    if body and not title:
        title = body
        body = None

    time_val = raw.get("time", int(datetime.now().timestamp() * 1000))
    url = raw.get("url") or raw.get("link")

    return NewsMessage(
        id=raw.get("_id", f"bwe-{time_val}"),
        title=title,
        body=body,
        url=url,
        symbols=parse_symbols(raw.get("symbols")),
        time=time_val,
        source="bwe",
    )


TRANSFORMERS: dict[FeedKey, Callable[[dict], NewsMessage | None]] = {
    "toa": transform_toa,
    "phx": transform_phx,
    "bwe": transform_bwe,
}


class FeedConnection:
    def __init__(
        self,
        config: FeedConfig,
        on_message: Callable[[NewsMessage], None],
        on_status: Callable[[FeedKey, bool], None],
    ):
        self.config = config
        self.on_message = on_message
        self.on_status = on_status
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.running = False
        self.reconnect_delay = 5.0
        self.max_reconnect_delay = 60.0

    async def connect(self):
        self.running = True
        asyncio.create_task(self._connect_loop())

    async def _connect_loop(self):
        while self.running:
            try:
                async with websockets.connect(self.config.url) as ws:
                    self.ws = ws
                    self.reconnect_delay = 5.0
                    self.on_status(self.config.key, True)
                    print(f"[{self.config.key}] Connected")

                    heartbeat_task = asyncio.create_task(self._heartbeat())
                    read_task = asyncio.create_task(self._read_messages())

                    done, pending = await asyncio.wait(
                        [heartbeat_task, read_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in pending:
                        task.cancel()

            except Exception as e:
                print(f"[{self.config.key}] Connection error: {e}")

            self.on_status(self.config.key, False)
            print(f"[{self.config.key}] Disconnected, reconnecting in {self.reconnect_delay}s")

            if self.running:
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(
                    self.reconnect_delay * 2, self.max_reconnect_delay
                )

    async def _heartbeat(self):
        while self.running and self.ws:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                if self.ws:
                    await self.ws.send("ping")
            except ConnectionClosed:
                break
            except Exception as e:
                print(f"[{self.config.key}] Heartbeat error: {e}")
                break

    async def _read_messages(self):
        if not self.ws:
            return

        transformer = TRANSFORMERS[self.config.key]

        try:
            async for message in self.ws:
                if message == "pong":
                    continue

                try:
                    raw = json.loads(message)
                    news = transformer(raw)
                    if news:
                        self.on_message(news)
                except json.JSONDecodeError:
                    continue
        except ConnectionClosed:
            pass
        except Exception as e:
            print(f"[{self.config.key}] Read error: {e}")

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()


class FeedAggregator:
    def __init__(self):
        self.connections: dict[FeedKey, FeedConnection] = {}
        self.feed_status: dict[FeedKey, bool] = {k: False for k in FEED_CONFIGS}
        self.message_callbacks: list[Callable[[NewsMessage], None]] = []
        self.recent_messages: list[NewsMessage] = []
        self.max_recent = 100

    def add_message_callback(self, callback: Callable[[NewsMessage], None]):
        self.message_callbacks.append(callback)

    def remove_message_callback(self, callback: Callable[[NewsMessage], None]):
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)

    def _on_message(self, msg: NewsMessage):
        self.recent_messages.insert(0, msg)
        if len(self.recent_messages) > self.max_recent:
            self.recent_messages = self.recent_messages[: self.max_recent]

        for callback in self.message_callbacks:
            try:
                callback(msg)
            except Exception as e:
                print(f"Callback error: {e}")

    def _on_status(self, key: FeedKey, connected: bool):
        self.feed_status[key] = connected

    async def start(self):
        for key, config in FEED_CONFIGS.items():
            conn = FeedConnection(config, self._on_message, self._on_status)
            self.connections[key] = conn
            await conn.connect()

        print("All feeds started")

    async def stop(self):
        for conn in self.connections.values():
            await conn.stop()

    def get_recent_for_feeds(self, feeds: set[FeedKey]) -> list[dict]:
        return [
            msg.to_dict() for msg in self.recent_messages if msg.source in feeds
        ]


aggregator = FeedAggregator()
