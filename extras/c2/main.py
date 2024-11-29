import asyncio
from threading import Thread
from connecter import WebSocketClient
from app import TankGameApp
# from renderer import GameRenderer

# Global WebSocket client
ws_client = None

def connect_to_server(player_name):
    """Callback to connect to the server with the player's name."""
    global ws_client
    try:
        asyncio.run(ws_client.connect(player_name, print))
        return ws_client.is_connected
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return False

def send_message_to_server(message):
    """Callback to send a message to the server."""
    global ws_client
    asyncio.run(ws_client.send(message))

def start_renderer():
    """Run the Pygame renderer after Tkinter exits."""
    # renderer = GameRenderer()
    # renderer.run()
    print("Inside Renderer")

async def websocket_listener():
    """Listen for WebSocket messages in the background."""
    global ws_client
    await ws_client.listen(message_callback)

def message_callback(data):
    """Process messages received from the WebSocket server."""
    if data.get("type") == "start-game":
        print("Game is starting...")

def run_tkinter():
    """Run the Tkinter GUI."""
    app = TankGameApp(connect_callback=connect_to_server, send_message_callback=send_message_to_server)
    app.run()  # Runs the Tkinter mainloop()

def main():
    global ws_client
    ws_client = WebSocketClient("ws://localhost:8000/ws")  # Replace with your WebSocket server URI

    # Start the WebSocket listener in the background
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(websocket_listener())

    # Run the Tkinter GUI on the main thread
    run_tkinter()

    # After Tkinter closes, start the Pygame renderer
    start_renderer()

    # Close WebSocket connection when done
    loop.run_until_complete(ws_client.connection.close())

if __name__ == "__main__":
    main()
