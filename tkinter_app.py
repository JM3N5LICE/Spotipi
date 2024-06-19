import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import threading

# Load environment variables from .env file
load_dotenv()

# Get environment variables
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Create a SpotifyOAuth object
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope='user-modify-playback-state user-read-playback-state')

# Get the token
token_info = sp_oauth.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token_info)

class MultiPageApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.configure(bg='gray20')  # Set the background color of the main window
        self.container = tk.Frame(self, bg='gray20')
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.page_order = ["Page1", "Page2", "Page3"]

        # Apply styles
        self.apply_styles()

        for PageClass in (Page1, Page2, Page3):
            page_name = PageClass.__name__
            page = PageClass(self.container, self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("Page1")

        self.current_page_index = 0

        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.end_drag)

        self.drag_start_x = 0

        # Add a button to launch the web page
        launch_button = tk.Button(self, text="Open Web Page", command=self.launch_web_page, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        launch_button.pack(side="bottom", pady=10)

        # Make the window full screen
        try:
            self.state('zoomed')  # For Windows
        except:
            self.attributes('-fullscreen', True)  # Cross-platform fullscreen

        # Center the window on the screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

    def start_drag(self, event):
        self.drag_start_x = event.x

    def do_drag(self, event):
        pass

    def end_drag(self, event):
        drag_end_x = event.x
        drag_distance = drag_end_x - self.drag_start_x

        if drag_distance > 100:
            self.current_page_index = max(0, self.current_page_index - 1)
        elif drag_distance < -100:
            self.current_page_index = min(len(self.page_order) - 1, self.current_page_index + 1)

        self.show_page(self.page_order[self.current_page_index])

    def launch_web_page(self):
        webbrowser.open('http://127.0.0.1:8888')

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        background="#4CAF50",
                        foreground="white",
                        font=("Helvetica", 12, "bold"),
                        padding=10)
        style.map("TButton",
                  background=[('active', '#45a049')])

        style.configure("TLabel",
                        font=("Helvetica", 16),
                        foreground="white",  # Change text color to white
                        background='gray20')  # Change background to match the main window

        style.configure("Treeview",
                        background="#D3D3D3",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#D3D3D3")
        style.map("Treeview",
                  background=[('selected', '#347083')])

        style.configure("Treeview.Heading",
                        font=("Helvetica", 14, "bold"),
                        background="#D3D3D3")

class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')  # Set background color
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        label = ttk.Label(self, text="Page 1: Time Display", style="TLabel")
        label.grid(row=0, column=0, pady=10, sticky="n")

        self.time_label = tk.Label(self, text="", font=("Helvetica", 48), fg="white", bg="gray20")
        self.time_label.grid(row=1, column=0, pady=20, sticky="n")

        self.update_time()

        button = ttk.Button(self, text="Go to Page 2", command=lambda: controller.show_page("Page2"))
        button.grid(row=2, column=0, pady=10, sticky="s")

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')  # Set background color
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        label = ttk.Label(self, text="Page 2: Music Control", style="TLabel")
        label.grid(row=0, column=0, pady=10, sticky="n")

        # Load and resize custom icons from the images folder
        self.play_icon = self.load_and_resize_icon("images/play2.png", 50, 50)
        self.pause_icon = self.load_and_resize_icon("images/pause2.png", 50, 50)
        self.skip_icon = self.load_and_resize_icon("images/skip.png", 50, 50)
        self.prev_icon = self.load_and_resize_icon("images/previous.png", 50, 50)

        # Create buttons with custom icons
        button_play = ttk.Button(self, image=self.play_icon, command=self.play_music)
        button_play.grid(row=1, column=0, pady=10, sticky="n")

        button_pause = ttk.Button(self, image=self.pause_icon, command=self.pause_music)
        button_pause.grid(row=2, column=0, pady=10, sticky="n")

        button_skip = ttk.Button(self, image=self.skip_icon, command=self.skip_music)
        button_skip.grid(row=3, column=0, pady=10, sticky="n")

        button_prev = ttk.Button(self, image=self.prev_icon, command=self.prev_music)
        button_prev.grid(row=4, column=0, pady=10, sticky="n")

    def load_and_resize_icon(self, path, width, height):
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def play_music(self):
        sp.start_playback()
        print("Playing music...")

    def pause_music(self):
        sp.pause_playback()
        print("Pausing music...")

    def skip_music(self):
        sp.next_track()
        print("Skipping to next track...")

    def prev_music(self):
        sp.previous_track()
        print("Going to previous track...")

class Page3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')  # Set background color
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)

        playlist_frame = tk.Frame(self, bg='gray20')
        playlist_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        track_frame = tk.Frame(self, bg='gray20')
        track_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        columns = ("Playlist Name",)
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=columns, show='headings', style="Custom.Treeview")
        self.playlist_tree.heading("Playlist Name", text="Playlist Name")
        self.playlist_tree.pack(expand=True, fill='both')

        self.playlist_tree.bind('<<TreeviewSelect>>', self.on_playlist_select)

        columns = ("Track Name",)
        self.track_tree = ttk.Treeview(track_frame, columns=columns, show='headings', style="Custom.Treeview")
        self.track_tree.heading("Track Name", text="Track Name")
        self.track_tree.pack(expand=True, fill='both')

        self.track_tree.bind('<<TreeviewSelect>>', self.on_track_select)

        self.song_label = tk.Label(self, text="Currently Playing: Song Name - Artist", font=("Helvetica", 20), fg="white", bg="gray20")
        self.song_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="s")

        self.load_playlists()

    def load_playlists(self):
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            self.playlist_tree.insert("", "end", values=(playlist['name'],), tags=(playlist['id'],))

    def on_playlist_select(self, event):
        selected_item = self.playlist_tree.selection()[0]
        playlist_id = self.playlist_tree.item(selected_item, "tags")[0]
        threading.Thread(target=self.load_tracks, args=(playlist_id,)).start()

    def load_tracks(self, playlist_id):
        self.track_tree.delete(*self.track_tree.get_children())
        self.tracks_list = []
        offset = 0
        limit = 100  # Number of items to fetch per request

        while True:
            tracks = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
            if not tracks['items']:
                break
            
            for track in tracks['items']:
                if track['track'] is not None:  # Check if track is not None
                    self.tracks_list.append(track['track']['uri'])
                    self.track_tree.insert("", "end", values=(track['track']['name'],), tags=(track['track']['uri'],))
            
            offset += len(tracks['items'])
            if len(tracks['items']) < limit:
                break  # If less than limit, we have fetched all tracks

        self.current_playlist_id = playlist_id
        print(f"Total tracks loaded: {len(self.tracks_list)}")

    def on_track_select(self, event):
        selected_item = self.track_tree.selection()[0]
        track_uri = self.track_tree.item(selected_item, "tags")[0]
        self.play_track(track_uri)

    def play_track(self, track_uri):
        start_index = self.tracks_list.index(track_uri)
        sp.start_playback(uris=self.tracks_list[start_index:])
        print(f"Playing track {track_uri}...")

def startTkinter():
    app = MultiPageApp()
    app.mainloop()

if __name__ == "__main__":
    startTkinter()
