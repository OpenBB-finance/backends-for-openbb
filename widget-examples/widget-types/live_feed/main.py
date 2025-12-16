import json
import asyncio
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketState
import websockets as ws_client
from websockets.exceptions import ConnectionClosed

from feeds import aggregator, NewsMessage, FeedKey

ROOT_PATH = Path(__file__).parent.resolve()
ALL_FEEDS: set[FeedKey] = {"toa", "phx", "bwe"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await aggregator.start()
    yield
    await aggregator.stop()


app = FastAPI(lifespan=lifespan)

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "https://pro.openbb.dev",
    "http://localhost:1420",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "name": "Live News Feed",
        "description": "Real-time news aggregator from BWE, Phoenix, and TreeOfAlpha",
        "endpoints": {
            "websocket": "/ws",
            "initial_data": "/news",
            "widgets": "/widgets.json",
        },
    }


@app.get("/widgets.json")
def get_widgets():
    return JSONResponse(content=json.load((ROOT_PATH / "widgets.json").open()))


def parse_feeds_param(feeds_param: str | None) -> set[FeedKey]:
    if not feeds_param:
        return ALL_FEEDS.copy()

    feeds = set()
    for f in feeds_param.split(","):
        f = f.strip().lower()
        if f in ALL_FEEDS:
            feeds.add(f)

    return feeds if feeds else ALL_FEEDS.copy()


@app.get("/news")
def get_news(feeds: str | None = None):
    """Initial data endpoint - returns recent messages for selected feeds"""
    selected_feeds = parse_feeds_param(feeds)
    messages = aggregator.get_recent_for_feeds(selected_feeds)

    return [
        {
            "id": msg["id"],
            "time": msg["time"],
            "source": msg["source"].upper(),
            "title": msg["title"],
            "url": msg.get("url", ""),
            "symbols": msg.get("symbols", []),
        }
        for msg in messages[:50]
    ]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "feeds": {k: v for k, v in aggregator.feed_status.items()},
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket_handler(websocket)
    except WebSocketDisconnect:
        return
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass


async def websocket_handler(websocket: WebSocket):
    subscribed_feeds: set[FeedKey] = ALL_FEEDS.copy()
    message_queue: asyncio.Queue[NewsMessage] = asyncio.Queue()

    def on_message(msg: NewsMessage):
        if msg.source in subscribed_feeds:
            try:
                message_queue.put_nowait(msg)
            except asyncio.QueueFull:
                pass

    aggregator.add_message_callback(on_message)

    try:
        consumer_task = asyncio.create_task(
            consumer_handler(websocket, subscribed_feeds)
        )
        producer_task = asyncio.create_task(
            producer_handler(websocket, message_queue)
        )

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    finally:
        aggregator.remove_message_callback(on_message)


async def consumer_handler(websocket: WebSocket, subscribed_feeds: set[FeedKey]):
    """Listen for subscription updates from client"""
    try:
        async for data in websocket.iter_json():
            if feeds := data.get("params", {}).get("feeds"):
                if isinstance(feeds, str):
                    feeds = feeds.split(",")

                subscribed_feeds.clear()
                for f in feeds:
                    f = f.strip().lower()
                    if f in ALL_FEEDS:
                        subscribed_feeds.add(f)

                if not subscribed_feeds:
                    subscribed_feeds.update(ALL_FEEDS)

                print(f"Client subscribed to: {subscribed_feeds}")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Consumer error: {e}")


async def producer_handler(websocket: WebSocket, queue: asyncio.Queue[NewsMessage]):
    """Send messages to client"""
    try:
        while websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json(
                    {
                        "id": msg.id,
                        "time": msg.time,
                        "source": msg.source.upper(),
                        "title": msg.title,
                        "url": msg.url or "",
                        "symbols": msg.symbols,
                    }
                )
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Producer error: {e}")


BINANCE_FUTURES_WS = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
DEFAULT_MIN_NOTIONAL = 100_000


@app.websocket("/ws/trades")
async def trades_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await trades_websocket_handler(websocket)
    except WebSocketDisconnect:
        return
    except Exception as e:
        print(f"Trades WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass


async def trades_websocket_handler(websocket: WebSocket):
    min_notional = DEFAULT_MIN_NOTIONAL
    trade_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=1000)
    running = True

    async def binance_listener():
        nonlocal running
        reconnect_delay = 5.0

        while running:
            try:
                async with ws_client.connect(BINANCE_FUTURES_WS) as binance_ws:
                    print("[trades] Connected to Binance Futures")
                    reconnect_delay = 5.0

                    async for message in binance_ws:
                        if not running:
                            break
                        try:
                            data = json.loads(message)
                            price = float(data["p"])
                            qty = float(data["q"])
                            notional = price * qty

                            if notional >= min_notional:
                                trade = {
                                    "id": str(uuid.uuid4()),
                                    "time": data["T"],
                                    "price": price,
                                    "quantity": qty,
                                    "notional": round(notional, 2),
                                    "side": "SELL" if data["m"] else "BUY",
                                }
                                try:
                                    trade_queue.put_nowait(trade)
                                except asyncio.QueueFull:
                                    pass
                        except (json.JSONDecodeError, KeyError):
                            continue

            except ConnectionClosed:
                print("[trades] Binance connection closed")
            except Exception as e:
                print(f"[trades] Binance error: {e}")

            if running:
                print(f"[trades] Reconnecting in {reconnect_delay}s")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60.0)

    async def client_consumer():
        nonlocal min_notional
        try:
            async for data in websocket.iter_json():
                if params := data.get("params", {}):
                    if "min_notional" in params:
                        try:
                            min_notional = float(params["min_notional"])
                            print(f"[trades] Min notional set to: ${min_notional:,.0f}")
                        except (ValueError, TypeError):
                            pass
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[trades] Consumer error: {e}")

    async def client_producer():
        try:
            while websocket.client_state != WebSocketState.DISCONNECTED:
                try:
                    trade = await asyncio.wait_for(trade_queue.get(), timeout=1.0)
                    await websocket.send_json(trade)
                except asyncio.TimeoutError:
                    continue
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[trades] Producer error: {e}")

    binance_task = asyncio.create_task(binance_listener())
    consumer_task = asyncio.create_task(client_consumer())
    producer_task = asyncio.create_task(client_producer())

    try:
        done, pending = await asyncio.wait(
            [binance_task, consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    finally:
        running = False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5050)
