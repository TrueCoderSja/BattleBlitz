import tkinter as tk
from tkinter import messagebox

class TankGameApp:
    def __init__(self, connect_callback, send_message_callback):
        """
        Initialize the TankGameApp.
        :param connect_callback: Function to connect to the server with player name.
        :param send_message_callback: Function to send messages to the server.
        """
        self.connect_callback = connect_callback
        self.send_message_callback = send_message_callback

        self.root = tk.Tk()
        self.root.title("Tank Game")

        # Variables for user inputs
        self.player_name = tk.StringVar()
        self.room_name = tk.StringVar()

    def show_connect_screen(self):
        """Show the initial screen to connect to the server."""
        self.clear_screen()

        tk.Label(self.root, text="Enter Player Name:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.player_name).pack(pady=10)
        tk.Button(self.root, text="Connect", command=self.connect_to_server).pack(pady=10)
        tk.Button(self.root, text="Close App", command=self.closeApp).pack()

    def closeApp(self):
        self.root.destroy()

    def show_room_screen(self):
        """Show the screen for creating or joining a room."""
        self.clear_screen()

        tk.Label(self.root, text="Enter Room Name:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.room_name).pack(pady=10)

        tk.Button(self.root, text="Create Room", command=self.create_room).pack(pady=5)
        tk.Button(self.root, text="Join Room", command=self.join_room).pack(pady=5)
        tk.Button(self.root, text="Start Game", command=self.start_game).pack(pady=5)

    def clear_screen(self):
        """Clear the current screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def connect_to_server(self):
        """Handle the connection to the server."""
        player_name = self.player_name.get().strip()
        if not player_name:
            messagebox.showerror("Error", "Player name cannot be empty!")
            return

        # Call the connect callback
        success = self.connect_callback(player_name)
        if success:
            messagebox.showinfo("Success", f"Connected as {player_name}")
            self.show_room_screen()
        else:
            messagebox.showerror("Error", "Failed to connect to server!")

    def create_room(self):
        """Handle creating a room."""
        room_name = self.room_name.get().strip()
        if not room_name:
            messagebox.showerror("Error", "Room name cannot be empty!")
            return

        self.send_message_callback({"type": "newroom", "roomname": room_name})
        messagebox.showinfo("Room Created", f"Room '{room_name}' created!")

    def join_room(self):
        """Handle joining a room."""
        room_name = self.room_name.get().strip()
        if not room_name:
            messagebox.showerror("Error", "Room name cannot be empty!")
            return

        self.send_message_callback({"type": "joinroom", "roomname": room_name})
        messagebox.showinfo("Room Joined", f"Joined room '{room_name}'")

    def start_game(self):
        """Send the start game message and exit Tkinter."""
        self.send_message_callback({"type": "startgame"})
        messagebox.showinfo("Starting Game", "Game is starting...")
        self.root.quit()  # Exit Tkinter

    def run(self):
        """Run the Tkinter main loop."""
        self.show_connect_screen()
        self.root.mainloop()
