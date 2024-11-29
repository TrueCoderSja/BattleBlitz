import websockets
import json

class WebSocketClient:
    def __init__(self, uri, message_callback, set_uid_cb):
        self.uri = uri
        self.message_callback = message_callback
        self.websocket = None
        self.running = False
        self.set_uid_cb=set_uid_cb

    async def connect(self, playername):
        self.websocket = await websockets.connect(self.uri)
        await self.websocket.send(json.dumps({
            "type":"connect",
            "playername":playername
        }))
        cnd_msg=await self.websocket.recv()
        cnd_data=json.loads(cnd_msg)
        self.uid=cnd_data["uid"]
        self.token=cnd_data["token"]
        print("Your UID: ", self.uid)
        self.set_uid_cb(self.uid)
        self.running = True
        await self.listen_for_messages()

    async def listen_for_messages(self):
        print("Listening for messages...")
        try:
            while self.running:
                message = await self.websocket.recv()
                self.message_callback(message)
        except websockets.ConnectionClosed:
            self.message_callback("Connection closed")
        except Exception as e:
            self.message_callback(f"Error: {e}")
        finally:
            self.running = False

    async def connectUser(self):
        await self.send_message(json.dumps({
            "type": "connect",
            "playername": "ttest"
        }))

    async def send_message(self, message):
        print("Sending message...")
        if self.websocket and self.running:
            await self.websocket.send(message)

    async def send_data(self, data):
        # print("Sending message...")
        if self.websocket and self.running:
            data["token"]=self.token
            await self.websocket.send(json.dumps(data))

    def stop(self):
        self.running = False