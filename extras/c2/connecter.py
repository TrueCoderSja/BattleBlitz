# connecter.py
import asyncio
import websockets

class WebSocketHandler:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.keep_running = True

    async def connect(self, callback):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            await self.listen(callback)

    async def listen(self, callback):
        while self.keep_running:
            try:
                message = await self.websocket.recv()
                if callback:
                    callback(message)
            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break

    async def send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def stop(self):
        self.keep_running = False
