import tkinter as tk
from tkinter import messagebox

class TankGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiplayer Tank Game")
        # self.root.attributes('-fullscreen', True)  # Fullscreen mode
        self.root.wm_state('zoomed')
        
        self.main_menu()

    def main_menu(self):
        self.clear_screen()
        
        title_label = tk.Label(self.root, text="Enter Arena", font=("Times", 40, "bold"))
        title_label.pack(pady=50)
        
        new_room_btn = tk.Button(self.root, text="New Room", font=("Times", 20), command=self.new_room)
        new_room_btn.pack(pady=20)
        
        join_room_btn = tk.Button(self.root, text="Join Room", font=("Times", 20), command=self.join_room)
        join_room_btn.pack(pady=20)

    def new_room(self):
        self.clear_screen()
        
        map_label = tk.Label(self.root, text="Select a Map", font=("Times", 30, "bold"), fg="gray")
        map_label.pack(pady=30)

        # Placeholder for map selection
        map_name_label = tk.Label(self.root, text="Map Name", font=("Times", 20), fg="green")
        map_name_label.pack()
        
        map_desc_label = tk.Label(self.root, text="Map Description", font=("Times", 16), fg="brown")
        map_desc_label.pack(pady=10)
        
        create_room_btn = tk.Button(self.root, text="Create Room", font=("Times", 20), command=self.waiting_room, fg="lime")
        create_room_btn.pack(pady=20)

    def join_room(self):
        self.clear_screen()
        
        room_id_label = tk.Label(self.root, text="Your Room ID:", font=("Times", 20), fg="dark green")
        room_id_label.pack(pady=20)
        
        room_id_entry = tk.Entry(self.root, font=("Times", 16), fg="green")
        room_id_entry.pack(pady=10)
        
        enter_room_btn = tk.Button(self.root, text="Enter Room", font=("Times", 20), fg="dark green", command=lambda: self.waiting_for_host())
        enter_room_btn.pack(pady=20)

    def waiting_room(self):
        self.clear_screen()
        
        room_label = tk.Label(self.root, text="Players Joined:", font=("Times", 20, "bold"))
        room_label.pack(pady=20)

        players_list = tk.Listbox(self.root, font=("Times", 16))
        players_list.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Placeholder for demo
        players_list.insert(tk.END, "Player 1 (Host)")
        
        start_game_btn = tk.Button(self.root, text="Start Game", font=("Arial", 20), command=self.start_game)
        start_game_btn.pack(pady=20)

    def waiting_for_host(self):
        self.clear_screen()
        
        waiting_label = tk.Label(self.root, text="Waiting for the host to start the game...", font=("Arial", 20))
        waiting_label.pack(pady=50)
        
        leave_btn = tk.Button(self.root, text="Leave Room", font=("Arial", 20), command=self.main_menu)
        leave_btn.pack(pady=20)

    def start_game(self):
        messagebox.showinfo("Start Game", "The game is starting!")
        self.main_menu()  # Placeholder for transitioning to the game screen

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TankGameGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred : {e}")