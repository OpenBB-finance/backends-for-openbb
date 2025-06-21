"""WebSocket router and connection manager for Databento Live API."""

import asyncio
import json
import queue
import threading
import warnings
from datetime import datetime
from typing import Any, Optional

import databento as db
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pytz import timezone
from websockets.exceptions import ConnectionClosedOK
from openbb_databento.utils.database import CmeDatabase

# pylint: disable=W0612,R0902,R0912,R0913,R0914,R0915
# flake8: noqa: F841

warnings.filterwarnings("ignore", category=DeprecationWarning)

router = APIRouter(prefix="/live")


class ConnectionManager:
    """Manages WebSocket connections and subscriptions for Databento Live API."""
    def __init__(
        self,
        cme_database: CmeDatabase,
        connection_timeout: float = 15.0,
        retry_delay: float = 5.0,
        max_retries: int = 3,
    ):
        """Initialize a WebSocket connection manager for Databento Live API

        Args:
            api_key: Databento API key
            connection_timeout: Timeout in seconds for connection attempts
            retry_delay: Delay in seconds between connection retries
            max_retries: Maximum number of connection retry attempts
        """
        self.router = router

        # Client connections and subscriptions
        self.active_connections: set[WebSocket] = set()
        self.client_subscriptions: dict[WebSocket, set[str]] = {}
        self.symbol_subscribers: dict[str, set[WebSocket]] = {}

        # Threading and queuing
        self.message_queue = queue.Queue()
        self.master_stream_queues = set()
        self.processor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.lock = asyncio.Lock()
        self.thread_running = False
        self.loop = None

        # Configuration
        self.connection_timeout = connection_timeout
        self.retry_delay = retry_delay
        self.max_retries = max_retries

        # Databento client
        self.client = None
        self.database = cme_database
        self.api_key = cme_database._api_key

        # Message cache - stores the most recent message for each symbol
        self.message_cache: dict[str, dict[str, Any]] = {}
        self.message_cache_lock = threading.Lock()

        self.live_grid_assets = self.database.live_grid_assets
        self.names_map = self.live_grid_assets.set_index("continuous_symbol")["name"].to_dict()
        self.instrument_id_map = (
            self.live_grid_assets.set_index("instrument_id")["continuous_symbol"].to_dict()
        )
        self.asset_map = self.live_grid_assets.set_index("continuous_symbol")["asset"].to_dict()
        self.asset_class_map = (
            self.live_grid_assets.set_index("continuous_symbol")["asset_class"].to_dict()
        )

        # Register endpoints with the app
        self._setup_app_routes()

    def _setup_app_routes(self):
        """Configure the FastAPI app with routes and event handlers"""

        async def startup_event():
            # Start the Databento client on application startup
            await self.start_master_connection()

        self.router.add_event_handler("startup", startup_event)

        async def shutdown_event():
            await self.stop_master_connection()

        self.router.add_event_handler("shutdown", shutdown_event)

        @self.router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connect(websocket)
            try:
                while True:
                    try:
                        data = await websocket.receive_text()
                        symbols = json.loads(data).get("params", {}).get("symbol", [])
                        await self.update_client_symbols(websocket, symbols)
                    except (WebSocketDisconnect, ConnectionClosedOK):
                        break
                    except Exception as e:  # pylint: disable=broad-except
                        err_msg = f"Error processing WebSocket message: {e}"
                        self.database.logger.error(err_msg, exc_info=True)
            finally:
                await self.disconnect(websocket)

        @self.router.get("/symbology")
        async def get_symbology(asset_type: Optional[str] = None) -> list:  # pylint: disable=R0911
            """Get the symbology map from Databento client"""
            try:
                if asset_type == "equity":
                    equity_symbols = self.live_grid_assets.query(
                        "asset_class == 'Equity'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@equity_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]

                if asset_type == "fx":
                    fx_symbols = self.live_grid_assets.query(
                        "asset_class == 'Currency'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@fx_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]

                if asset_type == "interest_rates":
                    ir_symbols = self.live_grid_assets.query(
                        "asset_class == 'Interest Rate'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@ir_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]

                if asset_type == "metals":
                    metals_symbols = self.live_grid_assets.query(
                        "asset_class == 'Metals' or asset == 'HR'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@metals_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]

                if asset_type == "agriculture":
                    ag_symbols = self.live_grid_assets.query(
                        "asset_class == 'Commodity/Agriculture' and asset != 'HR'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@ag_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]
                if asset_type == "energy":
                    energy_symbols = self.live_grid_assets.query(
                        "asset_class == 'Energy'"
                    ).continuous_symbol.tolist()
                    return [
                        {"label": v, "value": k, "extraInfo": {"description": self.asset_map[k]}}
                        for k, v in self.live_grid_assets.query(
                            "continuous_symbol.isin(@energy_symbols)"
                        ).set_index("continuous_symbol")["name"].to_dict().items()
                    ]
                return [
                    {
                        "label": k,
                        "value": v,
                        "extraInfo": {
                            "description": self.asset_class_map[k],
                            "rightOfDescription": self.asset_map[k],
                        },
                    }
                    for k, v in self.live_grid_assets.set_index(
                        "continuous_symbol"
                    )["name"].to_dict().items()
                ]

            except Exception as e:  # pylint: disable=broad-except
                self.database.logger.error("Error getting symbology map: %s", e, exc_info=True)
                return [{"label": f"Error: {e}", "value": ""}]

        @self.router.get("/control/subscribe")
        async def control_subscribe(symbols: str):
            """Subscribe to symbols from external control"""
            syms = symbols.split(",") if isinstance(symbols, str) else symbols
            if not syms:
                return {"success": False, "message": "No symbols provided"}

            # Start the master connection if not already running
            if not self.is_running:
                await self.start_master_connection()

            # Add the symbols to a special control subscriber
            for symbol in syms:
                if symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()

            return {"success": True, "subscribed": syms}

        @self.router.get("/master_stream")
        async def master_stream_endpoint():
            """Stream raw data directly from the master connection"""

            async def event_generator():
                async for message in self.get_master_stream():
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps(message)}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                },
            )

        @self.router.get("/control/status")
        async def control_status():
            """Get the status of the WebSocket connection"""
            return {
                "connected": self.is_running and self.client is not None,
                "active_clients": len(self.active_connections),
                "subscribed_symbols": list(self.symbol_subscribers.keys()),
            }

        @self.router.get("/get_ws_data")
        async def get_messages(symbol: Optional[str] = None) -> list:
            """Get the latest data for specified symbols

            This endpoint returns the most recent message received for each symbol
            from the Databento stream. If a symbol hasn't received any messages yet,
            it returns a placeholder with default values.

            Args:
                symbol: Comma-separated list of symbols

            Returns:
                List of latest messages for each symbol
            """
            # Return empty list if there are no subscribed symbols

            symbols = symbol.split(",") if isinstance(symbol, str) and symbol else []

            # Return empty list if no symbols provided
            if not symbols:
                return []

            result: list = []
            current_time = (
                datetime.now(tz=timezone("America/Chicago"))
                .strftime("%Y-%m-%d %H:%M:%S")
            )

            with self.message_cache_lock:
                for sym in symbols:
                    # If we have cached data for this symbol, use it
                    if sym in self.message_cache:
                        result.append(self.message_cache[sym])
                    else:
                        # Otherwise return a placeholder with empty values
                        result.append(
                            {
                                "date": current_time,
                                "symbol": sym,
                                "name": self.names_map.get(sym, sym),
                                "size": 0,
                                "side": "",
                                "price": 0.0,
                            }
                        )

            return result

        @self.router.get("/control/unsubscribe")
        async def control_unsubscribe(symbols: str):
            """Unsubscribe from symbols from external control"""
            syms = symbols.split(",") if isinstance(symbols, str) else symbols
            if not syms:
                return {
                    "success": False,
                    "message": "No symbols provided",
                }

            to_unsubscribe = []
            for symbol in syms:
                if (
                    symbol in self.symbol_subscribers
                    and not self.symbol_subscribers[symbol]
                ):
                    to_unsubscribe.append(symbol)

            # Clean up the symbol subscribers dictionary
            for symbol in to_unsubscribe:
                if (
                    symbol in self.symbol_subscribers
                    and not self.symbol_subscribers[symbol]
                ):
                    del self.symbol_subscribers[symbol]

            return {"success": True, "unsubscribed": to_unsubscribe}

    async def get_master_stream(self):
        """
        Creates an async generator that yields messages directly from the master connection.
        This can be used to create streaming endpoints.

        Yields:
            dict: Raw messages from the Databento client
        """
        if not self.is_running:
            # Start the master connection if not already running
            await self.start_master_connection()

        # Create a new queue for this stream
        stream_queue = asyncio.Queue()

        # Add this queue to master stream queues
        self.master_stream_queues.add(stream_queue)

        try:
            while self.is_running:
                try:
                    # Wait for a message to be added to this stream's queue
                    message = await asyncio.wait_for(stream_queue.get(), timeout=30.0)

                    # Parse and yield the message
                    if isinstance(message, str):
                        try:
                            yield json.loads(message)
                        except json.JSONDecodeError:
                            yield {"error": "Invalid JSON", "raw": message}
                    else:
                        yield message

                    # Mark as processed
                    stream_queue.task_done()

                except asyncio.TimeoutError:
                    # Send a heartbeat to keep the connection alive
                    yield {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                except Exception as e:  # pylint: disable=broad-except
                    self.database.logger.error("Error in master stream: %s", e, exc_info=True)
                    yield {"error": str(e)}
                    await asyncio.sleep(1)
        finally:
            # Clean up when the stream ends
            if stream_queue in self.master_stream_queues:
                self.master_stream_queues.remove(stream_queue)

    def user_callback(self, record: db.DBNRecord) -> None:
        """Callback function for Databento record handling"""
        try:
            msg = {}

            if isinstance(record, db.TradeMsg):
                # Get the symbol from symbology map
                symbol = self.instrument_id_map.get(str(record.instrument_id))
                name = self.names_map.get(symbol)
                # Create the trade message
                msg = {
                    "date": record.pretty_ts_event.tz_convert(  # type: ignore
                        timezone("America/Chicago")
                    ).strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "symbol": symbol,
                    "name": name,
                    "side": (
                        "Ask"
                        if record.side == "A"
                        else "Bid" if record.side == "B" else "Neutral"
                    ),
                    "size": record.size,
                    "price": record.pretty_price,
                }

            if msg:
                # Update the message cache with this latest data
                with self.message_cache_lock:
                    self.message_cache[symbol] = msg  # type: ignore

                # Add to the message queue for processing
                self.message_queue.put(msg)

                # Also directly broadcast to master stream queues
                if self.master_stream_queues and self.loop:
                    for q in self.master_stream_queues:
                        asyncio.run_coroutine_threadsafe(q.put(msg), self.loop)

        except Exception as e:  # pylint: disable=broad-except
            self.database.logger.error("Error in user_callback: %s", e, exc_info=True)

    def error_handler(self, exception: Exception) -> None:
        """Error handler for Databento client"""
        self.database.logger.error("Databento error: %s", exception, exc_info=True)
        # Put a reconnection message in the queue
        self.message_queue.put({"_reconnect": True})

    def process_messages_thread(self):
        """Thread function to process messages from the queue"""
        asyncio.set_event_loop(self.loop)
        self.thread_running = True

        while self.thread_running:
            try:
                try:
                    message = self.message_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # Check if this is a reconnection signal
                if isinstance(message, dict) and message.get("_reconnect"):
                    asyncio.run_coroutine_threadsafe(self.reconnect(), self.loop) # type: ignore
                    self.message_queue.task_done()
                    continue

                # Process message
                try:
                    # Check if this is a trade message from Databento
                    if (
                        isinstance(message, dict)
                        and "symbol" in message
                        and "price" in message
                    ):
                        symbol = message.get("symbol")
                        if symbol and symbol in self.symbol_subscribers:
                            subscribers = self.symbol_subscribers[symbol].copy()
                            if subscribers:
                                asyncio.run_coroutine_threadsafe(
                                    self.broadcast_to_subscribers(subscribers, message),
                                    self.loop,  # type: ignore
                                )
                finally:
                    # Mark the message as processed
                    self.message_queue.task_done()
            except Exception as e:  # pylint: disable=broad-except
                self.database.logger.error("Error in message processor thread: %s", e, exc_info=True)

    async def broadcast_to_subscribers(self, subscribers: set[WebSocket], msg: dict):
        """Broadcast a message to all specified subscribers"""
        for client in subscribers:
            try:
                await client.send_json(msg)
            except Exception as e:  # pylint: disable=broad-except
                self.database.logger.error("Error sending to client: %s", e, exc_info=True)

    async def start_master_connection(self):
        """Start the Databento Live client connection"""
        # Don't reconnect if already running
        if self.is_running and self.client:
            return

        # Clean up any existing connection first
        await self.stop_master_connection()

        retries = 0
        while retries <= self.max_retries:
            try:
                self.database.logger.info(
                    "Starting Databento client (attempt %d/%d)...",
                    retries + 1, self.max_retries + 1
                )

                # Initialize the Databento client
                self.client = db.Live(self.api_key)

                # Store the event loop for the thread to use
                self.loop = asyncio.get_event_loop()

                # Start thread to process messages from the queue
                self.thread_running = True
                self.processor_thread = threading.Thread(
                    target=self.process_messages_thread, daemon=True
                )
                self.processor_thread.start()
                symbols = list(self.instrument_id_map.values())

                # Subscribe to all symbols
                self.client.subscribe(
                    dataset="GLBX.MDP3",
                    schema="trades",
                    stype_in="continuous",
                    symbols=symbols,
                )

                # Add callback function
                self.client.add_callback(
                    record_callback=self.user_callback,
                    exception_callback=self.error_handler,
                )

                # Start the client
                self.is_running = True
                self.client.start()

                self.database.logger.info("Databento master connection established")

                # Connection successful, exit retry loop
                break

            except Exception as e:  # pylint: disable=broad-except
                retries += 1
                if retries <= self.max_retries:
                    self.database.logger.warning(
                        "Connection error: %s, retrying in %s seconds...",
                        e, str(self.retry_delay)
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.database.logger.error(
                        "Failed to establish Databento connection: %s",
                        e,
                        exc_info=True
                    )
                    self.is_running = False
                    break

    async def stop_master_connection(self):
        """Stop the Databento client connection"""
        self.is_running = False

        # Stop the message processing thread
        if self.processor_thread and self.processor_thread.is_alive():
            self.thread_running = False
            self.processor_thread.join(timeout=2.0)
            self.processor_thread = None

        # Stop Databento client
        if self.client:
            try:
                self.client.stop()
            except Exception as e:  # pylint: disable=broad-except
                self.database.logger.error(
                    "Error stopping Databento client: %s",
                    e,
                    exc_info=True,
                )
            self.client = None

        # Clear the message queue
        while True:
            try:
                self.message_queue.get_nowait()
                self.message_queue.task_done()
            except queue.Empty:
                break

        self.database.logger.info("Databento master connection closed")

    async def reconnect(self):
        """Handle reconnection after a connection failure"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait a bit before reconnecting
        await asyncio.sleep(self.retry_delay)

        # Always reconnect, regardless of client connections
        await self.start_master_connection()

    async def connect(self, websocket: WebSocket):
        """Handle a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.client_subscriptions[websocket] = set()

        # Start the master connection if not already running
        if not self.is_running:
            await self.start_master_connection()

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

            # Remove client subscriptions
            if websocket in self.client_subscriptions:
                subscribed_symbols = self.client_subscriptions.pop(websocket)

                # Update symbol subscribers
                for symbol in subscribed_symbols:
                    if symbol in self.symbol_subscribers:
                        self.symbol_subscribers[symbol].discard(websocket)

            if websocket.application_state == 1:
                await websocket.close(reason="Client disconnected")

    async def update_client_symbols(self, websocket: WebSocket, symbols: list):
        """Update the symbols a client is subscribed to"""
        async with self.lock:
            if websocket not in self.active_connections:
                return

            if not symbols:
                return

            old_symbols = self.client_subscriptions.get(websocket, set())
            new_symbols = set(symbols)

            # Symbols to subscribe to
            to_subscribe = new_symbols - old_symbols

            # Symbols to unsubscribe from
            to_unsubscribe = old_symbols - new_symbols

            # Update client subscriptions
            self.client_subscriptions[websocket] = new_symbols

            # Update symbol subscribers
            for symbol in to_subscribe:
                if symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()
                self.symbol_subscribers[symbol].add(websocket)

            for symbol in to_unsubscribe:
                if symbol in self.symbol_subscribers:
                    self.symbol_subscribers[symbol].discard(websocket)


def create_databento_manager(
    api_key: Optional[str] = None,
    db_file: Optional[str] = None
) -> ConnectionManager:
    """Create a ConnectionManager configured for Databento Live API"""
    cme_database = CmeDatabase(api_key=api_key, db_file=db_file)
    return ConnectionManager(
        cme_database = cme_database,
        connection_timeout=30.0,
        retry_delay=5.0,
        max_retries=3,
    )
