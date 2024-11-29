import connecter
import asyncio
import threading
import json
import app
import renderer
import requests
import fileHandler
import time
import queue
import tkinter as tk

isInitailized=False
SERVER_ADD="decretpc:8000"
BASE_URL_HTTP="http://"+SERVER_ADD+"/"
BASE_URL_WS="ws://"+SERVER_ADD+"/ws"
ui_queue=queue.Queue()
ranks=[]

def setUID(uid):
    global uniqueID
    uniqueID=uid

def start_listening(playername):
    global ws_client
    # asyncio.run_coroutine_threadsafe(ws_client.connect(playername), asyncio.new_event_loop())
    threading.Thread(target=asyncio.run, args=(listen_forever(playername),), daemon=True).start()

async def listen_forever(playername):
    global ws_client
    await ws_client.connect(playername)

def onMessage(message):
    # print(message)
    global app, mapPath, tilemap_data, isInitailized
    data = json.loads(message)
    if "req" in data:
        req = data["req"]
        if req == "newroom":
            mapPath=tilemap_data[data["roomType"]]["extractedPath"]
            ui_queue.put(lambda: app.waiting_room(data["des"]))
        elif req == "joinroom":
            if data["success"]:
                mapPath=tilemap_data[data["roomType"]]["extractedPath"]
                ui_queue.put(lambda: app.waiting_for_host(data["des"]))
    elif "type" in data:
        type = data["type"]
        if type == "start-game":
            isInitailized=True
            ui_queue.put(lambda: app.closeUI())
        elif type == "new-member":
            ui_queue.put(lambda: app.addPlayerToRoom(data["des"]))
        elif type == "update-position":
            if isInitailized:
                try:
                    renderer.setPositions(data["positions"])
                except Exception as e:
                    print(f"Exception during position update: {e}")
        elif type=="death":
            print("Death {}".format(message))
            renderer.enableGraveMode()
        elif type=="finish":
            print("Finish event")
            global ranks
            ranks=data["des"]
            renderer.exitApp()



def process_queue():
    while not ui_queue.empty():
        task = ui_queue.get_nowait()
        try:
            task()
        except Exception as e:
            print(f"Error processing task: {e}")
    app.root.after(100, process_queue)


def send_data(data):
    # print("Sending message")
    if data:
        asyncio.run(ws_client.send_data(data))

def iniatialize_listener(playername):
    global ws_client, app
    ws_client = connecter.WebSocketClient(BASE_URL_WS, onMessage, setUID)
    start_listening(playername)

def updatePos(direction):
    send_data({
        "type": "updatePos",
        "direction": direction
    })

def preload(cb):
    global tilemap_data
    start_time = time.time()  # Record start time
    
    try:
        tilemapsURL = BASE_URL_HTTP + "tilemaps"
        response = requests.get(tilemapsURL)
        print("Preload complete")
        
        if not response.status_code == 200:
            print("Cannot make request")
            cb(None)
            return
        
        tilemap_data = response.json()

        for t in tilemap_data:
            tileMapURL = (BASE_URL_HTTP + "static/" + t["archivePath"]).replace("\\", "/")
            tileMapPath = fileHandler.fetch_tilemap_file(tileMapURL, t["name"])
            t["extractedPath"] = tileMapPath
            thumbnailURL = (BASE_URL_HTTP + "static/" + t["thumbnailPath"]).replace("\\", "/")
            thumbnailPath = fileHandler.fetch_file(thumbnailURL, t["name"] + ".png")
            t["thumbnailPath"] = thumbnailPath

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # If the operation finished early, sleep for the remaining time to make it last at least 3 seconds
        sleep_time = max(3 - elapsed_time, 0)  # Ensure no negative sleep time
        time.sleep(sleep_time)

        # Call the callback function with the tilemap data
        cb(tilemap_data)

    except Exception as e:
        print(e)
        cb(None)

def show_ranks_standalone():
    global ranks
    print("Inside show ranks: ",ranks)
    # Create a new root instance
    root = tk.Tk()
    root.title("Player Ranks")
    root.geometry("400x300")
    root.config(bg="#f0f0f0")
    root.resizable(False, False)
    root.wm_state('zoomed')

    # Create a label to display the title
    title_label = tk.Label(root, text="Player Ranks", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333333")
    title_label.pack(pady=20)

    # Create a frame for the rank list
    rank_list_frame = tk.Frame(root, bg="#f0f0f0")
    rank_list_frame.pack(fill="both", expand=True)

    # Loop through the ranks array and display each player's rank
    for idx, player in enumerate(ranks):
        rank_label = tk.Label(rank_list_frame, text=f"{idx+1}. {player}", font=("Helvetica", 14), fg="#333333", bg="#f0f0f0")
        rank_label.pack(pady=5)

    # Add a "Close" button at the bottom
    close_btn = tk.Button(
        root,
        text="Close",
        font=("Helvetica", 14),
        bg="#f44336",
        fg="white",
        activebackground="#e53935",
        activeforeground="white",
        relief="flat",
        command=root.destroy  # Destroy the window when clicked
    )
    close_btn.pack(pady=20)

    # Start the Tkinter main loop
    root.mainloop()

def main():
    global app, uniqueID, isInitailized, mapPath
    app=app.TankGameGUI(preload, iniatialize_listener, send_data)
    app.root.after(100, process_queue)
    app.root.mainloop()

    if isInitailized:
        renderer.init(uniqueID, mapPath, updatePos, lambda: ws_client.stop())
        isInitailized=True
        print("Initialized")
        try:
            renderer.updateloop()
            
            show_ranks_standalone()
        except Exception as e:
            print(e)
            
            show_ranks_standalone()

        print("Out of app")
        # show_ranks_standalone()

        

if __name__=="__main__":
    main()