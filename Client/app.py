import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from PIL import Image, ImageTk
import pyperclip
from audio import SoundManager

class TankGameGUI:
    def __init__(self, preload_cb, connect_cb, send_data_cb):
        self.audio_file = "background.ogg"  # Replace with your audio file path
        self.backgroundAudio=SoundManager(SoundManager.BACKGROUND)
        self.backgroundAudio.play()
        self.root = tk.Tk()
        self.connect_cb=connect_cb
        self.send_data_cb=send_data_cb
        self.preload_cb=preload_cb
        self.root.title("Multiplayer Tank Game")
        self.root.wm_state('zoomed')  # Fullscreen mode

        self.loadingScreen()

    def loadingScreen(self):
        self.clear_screen()

        self.background_image = Image.open("assets/loading.png")
        self.setup_background()

        # Add a progress bar
        progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate")
        x=(self.root.winfo_width()-300)//2
        y=self.root.winfo_height()-150
        progress_bar.place(x=x, y=y)

        # Start the dummy download in a background thread
        threading.Thread(target=self.preload_cb, args=(self.on_download_complete,), daemon=True).start()

        # Start the progress bar
        progress_bar.start()

    def on_download_complete(self, result):
        # Safely transition to the connect screen from the main thread
        self.animation_running = False  # Stop the GIF animation
        if result:
            self.tileMapData = result
            self.root.after(0, self.connect_screen)
        else:
            # Display an error dialog with Retry and Exit options
            print("Connection error...")
            self.root.after(0, lambda: self.show_error_with_retry("Error connecting to server."))

    def show_error_with_retry(self, message):
        self.root.bell()  # Play error sound

        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Connection Error")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f0f0")  # Light gray background

        # Center the dialog
        self.center_dialog(dialog, 300, 150)

        dialog.transient(self.root)  # Keep dialog on top
        dialog.grab_set()  # Make it modal

        # Error message
        error_label = tk.Label(
            dialog, text=message, font=("Helvetica", 14), fg="#333333", bg="#f0f0f0", wraplength=360
        )
        error_label.pack(pady=20)

        # Button container with elegant styling
        button_frame = tk.Frame(dialog, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Modern styled Retry button with rounded corners
        retry_btn = tk.Button(
            button_frame,
            text="Retry",
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            bd=1,
            relief="solid",
            padx=20,
            pady=5,
            command=lambda: self.retry_loading(dialog),
        )
        retry_btn.pack(side=tk.LEFT, padx=10)

        # Modern styled Exit button with rounded corners
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            font=("Helvetica", 12),
            bg="#f44336",
            fg="white",
            activebackground="#e53935",
            activeforeground="white",
            bd=1,
            relief="solid",
            padx=20,
            pady=5,
            command=lambda: self.exit_app(dialog),
        )
        exit_btn.pack(side=tk.LEFT, padx=10)

        # Remove the default window close button behavior
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.exit_app(dialog))

    def center_dialog(self, dialog, width, height):
        # Get the dimensions of the parent window
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()

        # Calculate the position for centering
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        # Position the dialog
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    def retry_loading(self, dialog):
        dialog.destroy()  # Close the error dialog
        self.loadingScreen()  # Restart the loading screen

    def exit_app(self, dialog):
        dialog.destroy()  # Close the error dialog
        self.closeUI()  # Close the main application

    def connect_screen(self):
        self.clear_screen()

        self.background_image=Image.open("assets/background.jpg")
        self.setup_background()

        # Set root background color to a modern light grey
        self.root.config(bg="#f0f0f0")

        # Create a frame with a subtle light background color for the container
        container_frame = tk.Frame(self.root, bg="#2C3E50", padx=30, pady=30)
        
        # Center the container frame vertically and horizontally
        container_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Player Name Label with softer color
        player_name_label = tk.Label(container_frame, text="Player Name:", font=("Helvetica", 18), bg="#2C3E50", fg="#7F8C8D")
        player_name_label.pack(pady=10)

        # Entry box with modern styling, including a subtle border and green focus highlight
        self.player_name_entry = tk.Entry(container_frame, font=("Helvetica", 16), fg="black", width=30, relief="flat", bd=2, highlightthickness=2, highlightcolor="#1ABC9C")
        self.player_name_entry.pack(pady=10)

        # Connect Button with a vibrant green color for a fresh, energetic feel
        connect_btn = tk.Button(
            container_frame, text="Connect", font=("Helvetica", 18),
            command=self.on_connect, bg="#1ABC9C", fg="white", relief="flat", width=20, height=2
        )
        connect_btn.pack(pady=20)



    def on_connect(self):
        player_name = self.player_name_entry.get()
        if not player_name.strip():
            messagebox.showwarning("Invalid Input", "Player name cannot be empty!")
            return
        self.playerName=player_name
        self.connect_cb(player_name)  # Call the provided callback with the player name
        self.main_menu()  # Proceed to main menu after connecting

    def main_menu(self):
        self.clear_screen()

        # Create a frame container for centering the elements
        container = tk.Frame(self.root, bg="#2C3E50", padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Title label with a modern font and color
        title_label = tk.Label(container, text="Enter Arena", font=("Helvetica Neue", 40, "bold"), fg="#ECF0F1", bg="#2C3E50")
        title_label.pack(pady=30)

        # New Room button with rounded corners and modern colors
        new_room_btn = tk.Button(container, text="New Room", font=("Helvetica Neue", 18), fg="white", bg="#1ABC9C", relief="flat", padx=20, pady=10, 
                                activebackground="#16A085", command=self.new_room)
        new_room_btn.pack(pady=20, fill="x")

        # Join Room button with similar styling
        join_room_btn = tk.Button(container, text="Join Room", font=("Helvetica Neue", 18), fg="white", bg="#3498DB", relief="flat", padx=20, pady=10,
                                activebackground="#2980B9", command=self.join_room)
        join_room_btn.pack(pady=20, fill="x")

    def new_room(self):
        self.clear_screen()

        # Dark theme background for a sleek look
        self.root.config(bg="#2C3E50")  # Slightly lighter dark gray background

        # Create a container frame to hold the main content (Title, Map, Description, Create Room button)
        container = tk.Frame(self.root, bg="#2C3E50", padx=50, pady=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Title label with a modern font
        map_label = tk.Label(
            container,
            text="Select a Map",
            font=("Helvetica Neue", 30, "bold"),
            fg="#ECF0F1",  # Light gray text
            bg="#2C3E50"   # Match background
        )
        map_label.pack(pady=20)

        # Frame for the map display (inside the container frame)
        display_frame = tk.Frame(container, bg="#2C3E50")
        display_frame.pack(fill="x", expand=True)

        # Placeholder for map display image (can be set dynamically)
        self.display_image_label = tk.Label(display_frame, bg="#2C3E50")
        self.display_image_label.pack()

        # Map name label with modern font and color
        self.map_name_label = tk.Label(
            display_frame,
            text="Map Name",
            font=("Helvetica Neue", 24, "bold"),
            fg="#1ABC9C",  # Teal color
            bg="#2C3E50",
            anchor="center"
        )
        self.map_name_label.pack(pady=(20, 10))

        # Map description label with a light gray font for description text
        self.map_desc_label = tk.Label(
            display_frame,
            text="Map Description",
            font=("Helvetica Neue", 16),
            fg="#BDC3C7",  # Light gray text for description
            bg="#2C3E50",
            anchor="center",
            justify="center",
            wraplength=600  # Allow long descriptions to wrap
        )
        self.map_desc_label.pack(pady=(10, 20))

        # Frame for the navigation buttons (outside the container and centered vertically)
        navigation_buttons_frame = tk.Frame(self.root, bg="#2C3E50")
        navigation_buttons_frame.place(relx=0.5, rely=0.7, anchor="center")  # Adjust the vertical position to avoid overlap

        # Previous button with modern styling, smaller size
        self.prev_button = tk.Button(
            navigation_buttons_frame,
            text="◀ Previous",
            font=("Helvetica Neue", 12),
            command=self.prev_map,
            fg="#1ABC9C",  # Modern teal color
            bg="#34495E",  # Dark gray button
            activebackground="#16A085",  # Teal on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=15, pady=8
        )
        self.prev_button.pack(side="left", padx=20)

        # Next button with modern teal styling, smaller size
        self.next_button = tk.Button(
            navigation_buttons_frame,
            text="Next ▶",
            font=("Helvetica Neue", 12),
            command=self.next_map,
            fg="#1ABC9C",  # Teal text
            bg="#34495E",  # Dark gray button
            activebackground="#16A085",  # Teal on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=15, pady=8
        )
        self.next_button.pack(side="right", padx=20)

        # Create Room button with modern teal and gray styling
        create_room_btn = tk.Button(
            container,
            text="Create Room",
            font=("Helvetica Neue", 20),
            command=self.selectMap,
            fg="#ECF0F1",  # Light gray text
            bg="#1ABC9C",  # Teal button
            activebackground="#16A085",  # Teal on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=20, pady=10
        )
        create_room_btn.pack(pady=20)

        # Initialize map index
        self.current_map_index = 0

        # Load initial map details (can be updated dynamically)
        self.loadMapDetails(self.current_map_index)

    def loadMapDetails(self, index):
        # Extract map details
        name = self.tileMapData[index]["name"]
        description = self.tileMapData[index]["description"]
        display_image_path = self.tileMapData[index]["thumbnailPath"]  # Assuming full-size image path

        # Update labels
        self.map_name_label.config(text=name)
        self.map_desc_label.config(text=description)

        # Update display image
        try:
            image = Image.open(display_image_path)
            image = image.resize((400, 300), Image.Resampling.LANCZOS)  # Larger display image
            photo = ImageTk.PhotoImage(image)
            self.display_image_label.config(image=photo)
            self.display_image_label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            print(f"Error loading image: {e}")
            self.display_image_label.config(
                text="No Image Available",
                image="",
                fg="#ff0000",  # Red text for error
                bg="#1e1e1e",
                font=("Times", 20, "bold")
            )

    def prev_map(self):
        # Go to the previous map in the list
        self.current_map_index = (self.current_map_index - 1) % len(self.tileMapData)
        self.loadMapDetails(self.current_map_index)

    def next_map(self):
        # Go to the next map in the list
        self.current_map_index = (self.current_map_index + 1) % len(self.tileMapData)
        self.loadMapDetails(self.current_map_index)

    def selectMap(self):
        self.mapPath=self.tileMapData[self.current_map_index]["extractedPath"]
        self.send_data_cb({
            "type":"newroom",
            "roomType":self.current_map_index
        })

    def join_room(self):
        self.clear_screen()

        # Create a container frame for the content
        container = tk.Frame(self.root, bg="#2C3E50", padx=50, pady=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Room ID label with modern styling
        room_id_label = tk.Label(
            container, 
            text="Enter Room ID:", 
            font=("Arial", 20, "bold"), 
            fg="#ECF0F1",  # Light gray text
            bg="#2C3E50"
        )
        room_id_label.pack(pady=30)

        # Entry field for Room ID
        self.room_id_entry = tk.Entry(
            container, 
            font=("Arial", 16), 
            fg="#2C3E50",  # Dark text
            bg="#BDC3C7",  # Light gray background
            relief="flat",
            bd=2,
            justify="center"
        )
        self.room_id_entry.pack(pady=20, fill=tk.X)

        # Enter Room button with sleek modern look
        enter_room_btn = tk.Button(
            container, 
            text="Enter Room", 
            font=("Arial", 20, "bold"), 
            fg="#ECF0F1",  # Light gray text
            bg="#27AE60",  # Green button
            activebackground="#2ECC71",  # Brighter green on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=20, pady=10,
            command=self.enter_room
        )
        enter_room_btn.pack(pady=20)

    def enter_room(self):
        room_id=self.room_id_entry.get()
        self.send_data_cb({
            "type":"joinroom",
            "roomId":room_id
        })

    
    def waiting_room(self, uid):
        self.clear_screen()

        # Container frame for centering all elements
        container = tk.Frame(self.root, bg="#2C3E50", padx=50, pady=30)
        container.place(relx=0.5, rely=0.5, anchor="center")  # Centering the frame both vertically and horizontally

        # Room label with modern font and color
        room_label = tk.Label(
            container, 
            text="Players Joined:", 
            font=("Helvetica Neue", 24, "bold"), 
            fg="#ECF0F1",  # Light gray text
            bg="#2C3E50"
        )
        room_label.grid(row=0, column=0, pady=10)

        # Players list with a modern design
        self.players_list = tk.Listbox(
            container, 
            font=("Helvetica Neue", 16),
            bg="#34495E",  # Dark gray background
            fg="#ECF0F1",  # Light gray text
            bd=0,  # No border
            highlightthickness=0,  # No focus border
            selectbackground="#16A085",  # Teal when selected
            selectforeground="#ECF0F1",  # White text when selected
        )
        self.players_list.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        self.players_list.insert(tk.END, self.playerName+" (You)")  # Placeholder

        # Room ID label with a clean, readable font
        self.room_id_label = tk.Label(
            container,
            text="Your Room ID: " + uid,
            font=("Helvetica Neue", 16),
            fg="#ECF0F1",
            bg="#2C3E50"
        )
        self.room_id_label.grid(row=2, column=0, pady=10)

        # Copy button with modern hover effects
        copy_button = tk.Button(
            container,
            text="Copy",
            font=("Helvetica Neue", 16),
            command=self.copy_room_id,
            fg="#ECF0F1",
            bg="#1ABC9C",  # Teal background
            activebackground="#16A085",  # Teal on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=20, pady=10
        )
        copy_button.grid(row=3, column=0, pady=10)

        # Start Game button with modern font and clean design
        start_game_btn = tk.Button(
            container,
            text="Start Game",
            font=("Helvetica Neue", 20, "bold"),
            command=self.start_game,
            fg="#ECF0F1",
            bg="#1ABC9C",  # Teal background
            activebackground="#16A085",  # Teal on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=20, pady=15
        )
        start_game_btn.grid(row=4, column=0, pady=20)

        # Configure grid layout to make sure it expands correctly
        container.grid_columnconfigure(0, weight=1)  # Allow the listbox to expand in width
        container.grid_rowconfigure(1, weight=1)     # Allow the listbox to expand in height

    def copy_room_id(self):
        room_id = self.room_id_label.cget("text").split(":")[1].strip()  # Extract the room ID from the label text
        pyperclip.copy(room_id)

    def addPlayerToRoom(self, playerName):
        self.players_list.insert(tk.END, playerName)

    def waiting_for_host(self, players):
        self.clear_screen()

        # Create a container frame for the content
        container = tk.Frame(self.root, bg="#2C3E50", padx=50, pady=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Waiting label for modern look
        waiting_label = tk.Label(
            container, 
            text="Waiting for the host to start the game...", 
            font=("Arial", 20), 
            fg="#ECF0F1",  # Light gray text
            bg="#2C3E50"
        )
        waiting_label.pack(pady=30)

        # Listbox for displaying players in the room
        players_label = tk.Label(
            container, 
            text="Players in Room:", 
            font=("Arial", 20, "bold"), 
            fg="#ECF0F1",  # Light gray text
            bg="#2C3E50"
        )
        players_label.pack(pady=(20, 10))

        self.players_list = tk.Listbox(container, font=("Arial", 16), height=5)
        self.players_list.pack(pady=10, fill=tk.BOTH, expand=True)

        # Placeholder for demo, this should be dynamically updated
        self.players_list.insert(tk.END, self.playerName+" (You)")

        for player in players:
            self.players_list.insert(tk.END, player["playername"])

        # Room ID label
        self.room_id_label = tk.Label(
            container, 
            text="Room ID: " + self.room_id, 
            font=("Arial", 16), 
            fg="#BDC3C7",  # Light gray text
            bg="#2C3E50"
        )
        self.room_id_label.pack(pady=10)

        # Leave button with a modern, sleek design
        leave_btn = tk.Button(
            container, 
            text="Leave Room", 
            font=("Arial", 20), 
            command=self.main_menu, 
            fg="#ECF0F1",  # Light gray text
            bg="#E74C3C",  # Red button
            activebackground="#C0392B",  # Darker red on hover
            activeforeground="#ECF0F1",  # White text on hover
            relief="flat",
            padx=20, pady=10
        )
        leave_btn.pack(pady=20)

    def start_game(self):
        # messagebox.showinfo("Start Game", "The game is starting!")
        # self.main_menu()  # Placeholder for transitioning to the game screen
        self.send_data_cb({"type":"start-game"})

    def clear_screen(self):
    # Clear all widgets except the background
        for widget in self.root.winfo_children():
            if widget is not self.bg_label:
                widget.destroy()

    def setup_background(self):
        self.root.update_idletasks()

        # Get the dimensions of the root window
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Resize the background image to fit the window
        resized_image = self.background_image.resize((width, height), Image.LANCZOS)
        bg_image_tk = ImageTk.PhotoImage(resized_image)

        # If the background label already exists, remove it
        if hasattr(self, 'bg_label'):
            self.bg_label.destroy()

        # Create the background label with the new image
        self.bg_label = tk.Label(self.root, image=bg_image_tk)
        self.bg_label.image = bg_image_tk  # Keep a reference to avoid garbage collection
        self.bg_label.place(relwidth=1, relheight=1)
        self.bg_label.lower()

    def closeUI(self):
        self.backgroundAudio.stop()
        self.root.withdraw()
        self.root.quit()