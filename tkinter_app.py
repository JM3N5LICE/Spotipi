import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import threading
import webbrowser
import time
import requests
import io
import base64

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
                        scope='user-modify-playback-state user-read-playback-state user-library-modify playlist-modify-public playlist-modify-private')

# Get the token
token_info = sp_oauth.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token_info)

def launch_web_page():
    webbrowser.open('http://127.0.0.1:8888')

class MultiPageApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.configure(bg='gray20')  # Set the background color of the main window
        self.container = tk.Frame(self, bg='gray20')
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.page_order = ["Page1", "Page2", "Page3", "Page4"]

        # Apply styles
        self.apply_styles()

        for PageClass in (Page1, Page2, Page3, Page4):
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

        # Make the window full screen
        try:
            self.state('zoomed')  # For Windows
        except tk.TclError as e:
            print(f"Error setting state to zoomed: {e}")
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

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        background="#4CAF50",
                        foreground="grey",
                        font=("Helvetica", 12, "bold"),
                        padding=10)
        style.map("TButton",
                  background=[('active', '#45a049')])

        style.configure("TLabel",
                        font=("Helvetica", 16),
                        foreground="grey",
                        background='gray20')

        style.configure("Treeview",
                        background="#D3D3D3",
                        foreground="black",
                        rowheight=30,
                        font=("Helvetica", 12))
        style.map("Treeview",
                  background=[('selected', '#347083')])

        style.configure("Treeview.Heading",
                        font=("Helvetica", 14, "bold"),
                        background="#D3D3D3")
        
        style.configure("Custom.Treeview", 
                        font=("Helvetica", 14),
                        rowheight=30)

class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        self.time_label = tk.Label(self, text="", font=("Helvetica", 50), fg="grey", bg="gray20")
        self.time_label.grid(row=3, column=0, pady=20, sticky="n")

        self.song_label = tk.Label(self, text="", font=("Helvetica", 16), fg="grey", bg="gray20")
        self.song_label.grid(row=4, column=0, pady=10, sticky="s")

        # Create menu buttons
        self.menu_frame = tk.Frame(self, bg="gray20")
        self.menu_frame.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        self.shutdown_button = tk.Button(self.menu_frame, text="Shutdown", command=self.shutdown, bg="#4CAF50", fg="grey", font=("Helvetica", 12, "bold"))
        self.switch_device_button = tk.Button(self.menu_frame, text="Switch Device", command=self.toggle_device_tree, bg="#4CAF50", fg="grey", font=("Helvetica", 12, "bold"))
        self.launch_web_page_button = tk.Button(self.menu_frame, text="Launch Web Page", command=self.launch_web_page, bg="#4CAF50", fg="grey", font=("Helvetica", 12, "bold"))

        self.menu_buttons = [self.shutdown_button, self.switch_device_button, self.launch_web_page_button]
        self.menu_visible = False

        for i, button in enumerate(self.menu_buttons):
            button.grid(row=i, column=0, pady=5)

        self.device_tree_frame = tk.Frame(self.menu_frame, bg="gray20")
        self.device_tree = ttk.Treeview(self.device_tree_frame, columns=("Device Name",), show='headings', style="Custom.Treeview")
        self.device_tree.heading("Device Name", text="Device Name")
        self.device_tree.column("Device Name", minwidth=0, width=200)
        self.device_tree.pack(expand=True, fill='both', side='left')

        self.device_scroll = ttk.Scrollbar(self.device_tree_frame, orient="vertical", command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=self.device_scroll.set)
        self.device_scroll.pack(side='right', fill='y')

        self.device_tree.bind('<<TreeviewSelect>>', self.on_device_select)
        self.device_tree_frame.grid(row=len(self.menu_buttons), column=0, pady=5)
        self.device_tree_frame.grid_remove()

        self.update_time()
        self.update_album_art_and_song()
        self.after(3000, self.update_periodically)

        # Add a hamburger menu button at the bottom
        self.menu_icon = Image.open("images/menu.png")
        self.menu_icon = self.menu_icon.resize((50, 50), Image.LANCZOS)
        self.menu_icon = ImageTk.PhotoImage(self.menu_icon)

        menu_button = tk.Button(self, image=self.menu_icon, command=self.toggle_menu_buttons, bg="#4CAF50", bd=2.5, relief="solid")
        menu_button.image = self.menu_icon
        menu_button.grid(row=5, column=0, pady=10)

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def update_album_art_and_song(self):
        current_track = sp.current_playback()
        if current_track and current_track['item']:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            self.song_label.config(text=f"{track_name} - {artist_name}")
        else:
            self.song_label.config(text="")

    def update_periodically(self):
        self.update_album_art_and_song()
        self.after(3000, self.update_periodically)

    def toggle_menu_buttons(self):
        if self.menu_visible:
            for button in self.menu_buttons:
                button.grid_remove()
        else:
            for i, button in enumerate(self.menu_buttons):
                button.grid(row=i, column=0, pady=5)
        self.menu_visible = not self.menu_visible

    def toggle_device_tree(self):
        if self.device_tree_frame.winfo_ismapped():
            self.device_tree_frame.grid_remove()
        else:
            self.device_tree.delete(*self.device_tree.get_children())
            self.load_devices()
            self.device_tree_frame.grid()

    def launch_web_page(self):
        webbrowser.open('http://127.0.0.1:8888')

    def shutdown(self):
        os.system("sudo poweroff")

    def show_devices(self):
        self.toggle_device_tree()

    def on_device_select(self, event):
        selected_item = self.device_tree.selection()[0]
        device_id = self.device_tree.item(selected_item, "tags")[0]
        self.transfer_playback(device_id)
        self.device_tree_frame.grid_remove()

    def load_devices(self):
        def fetch_devices():
            try:
                devices = sp.devices()
                device_list = devices.get('devices', [])

                for device in device_list:
                    device_id = device.get('id')
                    device_name = device.get('name', 'Unknown Device')
                    self.device_tree.insert("", "end", values=(device_name,), tags=(device_id,))
            except Exception as e:
                print(f"Error fetching devices: {e}")

        threading.Thread(target=fetch_devices).start()

    def transfer_playback(self, device_id):
        sp.transfer_playback(device_id)
        print(f"Transferred playback to device ID: {device_id}")

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        label = ttk.Label(self, text="Page 2: Music Control", style="TLabel")
        label.grid(row=0, column=0, pady=10, sticky="n")

        self.album_art_frame = tk.Frame(self, bg='#4CAF50', width=250, height=250)
        self.album_art_frame.grid(row=1, column=0, pady=10)
        self.album_art_frame.grid_propagate(False)

        self.album_art_label = tk.Label(self.album_art_frame, bg='#4CAF50')
        self.album_art_label.pack(expand=True, fill='both')

        control_frame = tk.Frame(self, bg='gray20')
        control_frame.grid(row=2, column=0, pady=10)

        self.play_icon = self.load_and_resize_icon("images/play2.png", 35, 35)
        self.pause_icon = self.load_and_resize_icon("images/pause2.png", 35, 35)
        self.skip_icon = self.load_and_resize_icon("images/skip.png", 35, 35)
        self.prev_icon = self.load_and_resize_icon("images/previous.png", 35, 35)

        self.button_prev = tk.Button(control_frame, image=self.prev_icon, command=self.prev_music, bg="gray20", bd=0)
        self.button_prev.grid(row=0, column=0, padx=10)

        self.button_play = tk.Button(control_frame, image=self.play_icon, command=self.play_music, bg="gray20", bd=0)
        self.button_play.grid(row=0, column=1, padx=10)

        self.button_pause = tk.Button(control_frame, image=self.pause_icon, command=self.pause_music, bg="gray20", bd=0)
        self.button_pause.grid(row=0, column=1, padx=10)
        self.button_pause.grid_remove()

        self.button_skip = tk.Button(control_frame, image=self.skip_icon, command=self.skip_music, bg="gray20", bd=0)
        self.button_skip.grid(row=0, column=3, padx=10)

        self.song_label = tk.Label(self, text="No music playing", font=("Helvetica", 16), fg="grey", bg="gray20")
        self.song_label.grid(row=3, column=0, pady=10, sticky="s")

        self.last_track_id = None

        self.placeholder_image = self.create_placeholder_image(250, 250)

        self.update_album_art_and_song()
        self.after(3000, self.update_periodically)

    def load_and_resize_icon(self, path, width, height):
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def play_music(self):
        sp.start_playback()
        self.update_button_state(play=True)
        print("Playing music...")

    def pause_music(self):
        sp.pause_playback()
        self.update_button_state(play=False)
        print("Pausing music...")

    def update_button_state(self, play):
        if play:
            self.button_play.grid_remove()
            self.button_pause.grid()
        else:
            self.button_pause.grid_remove()
            self.button_play.grid()

    def skip_music(self):
        sp.next_track()
        self.update_album_art_and_song()
        print("Skipping to next track...")

    def prev_music(self):
        sp.previous_track()
        self.update_album_art_and_song()
        print("Going to previous track...")

    def update_album_art_and_song(self):
        def fetch_album_art_and_song():
            try:
                current_track = sp.current_playback()
                if current_track and current_track['item']:
                    track_id = current_track['item']['id']
                    if track_id != self.last_track_id:
                        self.last_track_id = track_id
                        track_name = current_track['item']['name']
                        artist_name = current_track['item']['artists'][0]['name']
                        self.song_label.config(text=f"{track_name} - {artist_name}")

                        album_images = current_track['item']['album']['images']
                        if album_images:
                            album_art_url = album_images[0]['url']
                            self.display_album_art(album_art_url)

                    if current_track['is_playing']:
                        self.update_button_state(play=True)
                    else:
                        self.update_button_state(play=False)
                else:
                    self.song_label.config(text="No music playing")
                    self.album_art_label.config(image=self.placeholder_image)
                    self.update_button_state(play=False)
            except Exception as e:
                print(f"Error updating album art and song: {e}")

        fetch_album_art_and_song()

    def display_album_art(self, url):
        def fetch_album_art():
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                image_byt = response.content
                image_open = Image.open(io.BytesIO(image_byt))
                image_resized = image_open.resize((250, 250), Image.LANCZOS)
                album_art_image = ImageTk.PhotoImage(image_resized)
                self.album_art_label.config(image=album_art_image)
                self.album_art_label.image = album_art_image
            except requests.RequestException as e:
                print(f"Error fetching album art: {e}")

        threading.Thread(target=fetch_album_art).start()

    def create_placeholder_image(self, width, height):
        placeholder = Image.new('RGB', (width, height), 'grey')
        return ImageTk.PhotoImage(placeholder)

    def update_periodically(self):
        self.update_album_art_and_song()
        self.after(3000, self.update_periodically)

class Page3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)

        playlist_frame = tk.Frame(self, bg='gray20')
        playlist_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        track_frame = tk.Frame(self, bg='gray20')
        track_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background="black",
                        foreground="grey",
                        fieldbackground="black",
                        font=("Helvetica", 14),
                        bordercolor="#4CAF50",
                        borderwidth=2)
        style.map("Custom.Treeview",
                  background=[('selected', '#347083')])

        style.configure("Custom.Treeview.Heading",
                        background="black",
                        foreground="grey",
                        font=("Helvetica", 14, "bold"),
                        bordercolor="#4CAF50",
                        borderwidth=2)

        columns = ("Playlist Name",)
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=columns, show='headings', style="Custom.Treeview")
        self.playlist_tree.heading("Playlist Name", text="Playlist Name")
        self.playlist_tree.column("Playlist Name", minwidth=0, width=150)
        self.playlist_tree.pack(expand=True, fill='both', side='left')

        self.playlist_scroll = ttk.Scrollbar(playlist_frame, orient="vertical", command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=self.playlist_scroll.set)
        self.playlist_scroll.pack(side='right', fill='y')

        self.playlist_tree.bind('<<TreeviewSelect>>', self.on_playlist_select)

        columns = ("Track Name",)
        self.track_tree = ttk.Treeview(track_frame, columns=columns, show='headings', style="Custom.Treeview")
        self.track_tree.heading("Track Name", text="Track Name")
        self.track_tree.column("Track Name", minwidth=0, width=300)
        self.track_tree.pack(expand=True, fill='both', side='left')

        self.track_scroll = ttk.Scrollbar(track_frame, orient="vertical", command=self.track_tree.yview)
        self.track_tree.configure(yscrollcommand=self.track_scroll.set)
        self.track_scroll.pack(side='right', fill='y')

        self.track_tree.bind('<<TreeviewSelect>>', self.on_track_select)

        self.song_label = tk.Label(self, text="Currently Playing: Song Name - Artist", font=("Helvetica", 16), fg="grey", bg="gray20")
        self.song_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="s")

        self.load_playlists()

        # Initialize the last track ID
        self.last_track_id = None

        # Update the song label periodically
        self.update_song_label()
        self.after(3000, self.update_periodically)

    def load_playlists(self):
        def fetch_playlists():
            try:
                playlists = sp.current_user_playlists()
                for playlist in playlists['items']:
                    self.playlist_tree.insert("", "end", values=(playlist['name'],), tags=(playlist['id'],))
            except Exception as e:
                print(f"Error fetching playlists: {e}")

        threading.Thread(target=fetch_playlists).start()

    def on_playlist_select(self, event):
        selected_item = self.playlist_tree.selection()[0]
        playlist_id = self.playlist_tree.item(selected_item, "tags")[0]
        threading.Thread(target=self.load_tracks, args=(playlist_id,)).start()

    def load_tracks(self, playlist_id):
        def fetch_tracks():
            try:
                self.track_tree.delete(*self.track_tree.get_children())
                self.tracks_list = []
                offset = 0
                limit = 100

                while True:
                    tracks = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                    if not tracks['items']:
                        break
                    
                    for track in tracks['items']:
                        if track['track'] is not None:
                            track_uri = track['track']['uri']
                            track_name = track['track']['name']
                            artist_name = track['track']['artists'][0]['name']
                            display_text = f"{track_name} - {artist_name}"
                            self.tracks_list.append(track_uri)
                            self.track_tree.insert("", "end", values=(display_text,), tags=(track_uri,))
                    
                    offset += len(tracks['items'])
                    if len (tracks['items']) < limit:
                        break

                self.current_playlist_id = playlist_id
                print(f"Total tracks loaded: {len(self.tracks_list)}")
            except Exception as e:
                print(f"Error fetching tracks: {e}")

        threading.Thread(target=fetch_tracks).start()

    def on_track_select(self, event):
        selected_item = self.track_tree.selection()[0]
        track_uri = self.track_tree.item(selected_item, "tags")[0]
        self.play_track(track_uri)

    def play_track(self, track_uri):
        current_track = sp.current_playback()
        if not current_track or not current_track['is_playing']:
            self.launch_sdk_and_play(track_uri)
        else:
            playlist_uri = f"spotify:playlist:{self.current_playlist_id}"
            sp.start_playback(context_uri=playlist_uri, offset={"uri": track_uri})
            track_info = sp.track(track_uri)
            track_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            self.song_label.config(text=f"Currently Playing: {track_name} - {artist_name}")
            print(f"Playing track {track_uri}...")

    def launch_sdk_and_play(self, track_uri):
        # Launch the SDK in the web browser
        webbrowser.open('http://127.0.0.1:8888')
        time.sleep(5)  # Give some time for the SDK to initialize

        # Transfer playback to the SDK and play the track
        device_id = self.get_sdk_device_id()
        if device_id:
            sp.transfer_playback(device_id)
            sp.start_playback(uris=[track_uri])
            track_info = sp.track(track_uri)
            track_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            self.song_label.config(text=f"Currently Playing: {track_name} - {artist_name}")
            print(f"Playing track {track_uri} on SDK...")

    def get_sdk_device_id(self):
        devices = sp.devices().get('devices', [])
        for device in devices:
            if device['name'] == 'Web Playback SDK Quick Start Player':
                return device['id']
        return None

    def update_song_label(self):
        current_track = sp.current_playback()
        if current_track and current_track['item']:
            track_id = current_track['item']['id']
            if track_id != self.last_track_id:
                self.last_track_id = track_id
                track_name = current_track['item']['name']
                artist_name = current_track['item']['artists'][0]['name']
                self.song_label.config(text=f"Currently Playing: {track_name} - {artist_name}")
        else:
            self.song_label.config(text="Currently Playing: No music playing")

    def update_periodically(self):
        self.update_song_label()
        self.after(3000, self.update_periodically)

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def focus_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()

class Page4(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='gray20')
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        self.search_var = tk.StringVar()
        
        self.search_label = tk.Label(self, text="Search for a Song", font=("Helvetica", 16), fg="grey", bg="gray20")
        self.search_label.grid(row=0, column=1, pady=10, sticky="n")

        self.results_tree = ttk.Treeview(self, columns=("Song", "Artist"), show='headings', style="Custom.Treeview")
        self.results_tree.heading("Song", text="Song")
        self.results_tree.heading("Artist", text="Artist")
        self.results_tree.grid(row=1, column=0, columnspan=3, pady=10, padx=30, sticky="nsew")

        self.results_scroll = ttk.Scrollbar(self, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=self.results_scroll.set)
        self.results_scroll.grid(row=1, column=3, sticky='ns')

        self.search_entry = PlaceholderEntry(self, placeholder="Search a song or artist", textvariable=self.search_var, font=("Helvetica", 16))
        self.search_entry.grid(row=2, column=1, pady=10, sticky="ew", padx=10)

        self.playlist_tree = ttk.Treeview(self, columns=("Playlist Name",), show='headings', style="Custom.Treeview")
        self.playlist_tree.heading("Playlist Name", text="Playlist Name")
        self.playlist_tree.grid(row=1, column=3, rowspan=3, pady=10, padx=10, sticky="nsew")

        self.playlist_scroll = ttk.Scrollbar(self, orient="vertical", command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=self.playlist_scroll.set)
        self.playlist_scroll.grid(row=1, column=4, rowspan=3, sticky='ns')

        self.load_playlists()

        self.btn_frame = tk.Frame(self, bg="gray20")
        self.btn_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=10)

        self.search_button = tk.Button(self.btn_frame, text="Search", command=self.search_song, bg="#4CAF50", fg="grey", font=("Helvetica", 12, "bold"), height=1, width=20)
        self.search_button.pack(side="top", expand=True, fill="both", pady=5, padx=10)

        self.add_to_playlist_button = tk.Button(self.btn_frame, text="Add to Playlist", command=self.add_to_playlist, bg="#4CAF50", fg="grey", font=("Helvetica", 12, "bold"), height=1, width=20)
        self.add_to_playlist_button.pack(side="top", expand=True, fill="both", pady=5, padx=10)

        self.results_tree.bind('<<TreeviewSelect>>', self.on_song_select)
        self.playlist_tree.bind('<<TreeviewSelect>>', self.on_playlist_select)

        self.search_results = []
        self.selected_track_uri = None

    def load_playlists(self):
        def fetch_playlists():
            try:
                playlists = sp.current_user_playlists()
                for playlist in playlists['items']:
                    self.playlist_tree.insert("", "end", values=(playlist['name'],), tags=(playlist['id'],))
            except Exception as e:
                print(f"Error fetching playlists: {e}")

        threading.Thread(target=fetch_playlists).start()

    def search_song(self):
        def fetch_songs():
            query = self.search_var.get()
            if query:
                results = sp.search(q=query, type="track", limit=20)
                tracks = results.get('tracks', {}).get('items', [])

                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)

                self.search_results = []
                for track in tracks:
                    track_name = track['name']
                    artist_name = track['artists'][0]['name']
                    self.results_tree.insert("", "end", values=(track_name, artist_name), tags=(track['uri'],))
                    self.search_results.append(track)

        threading.Thread(target=fetch_songs).start()

    def on_song_select(self, event):
        selected_item = self.results_tree.selection()[0]
        track_uri = self.results_tree.item(selected_item, "tags")[0]
        self.selected_track_uri = track_uri
        self.play_track(track_uri)

    def play_track(self, track_uri):
        current_track = sp.current_playback()
        if not current_track or not current_track['is_playing']:
            self.launch_sdk_and_play(track_uri)
        else:
            sp.start_playback(uris=[track_uri])
            track_info = sp.track(track_uri)
            track_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            print(f"Playing track {track_uri}...")

    def launch_sdk_and_play(self, track_uri):
        # Launch the SDK in the web browser
        webbrowser.open('http://127.0.0.1:8888')
        time.sleep(5)  # Give some time for the SDK to initialize

        # Transfer playback to the SDK and play the track
        device_id = self.get_sdk_device_id()
        if device_id:
            sp.transfer_playback(device_id)
            sp.start_playback(uris=[track_uri])
            track_info = sp.track(track_uri)
            track_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            print(f"Playing track {track_uri} on SDK...")

    def get_sdk_device_id(self):
        devices = sp.devices().get('devices', [])
        for device in devices:
            if device['name'] == 'Web Playback SDK Quick Start Player':
                return device['id']
        return None

    def on_playlist_select(self, event):
        selected_item = self.playlist_tree.selection()[0]
        playlist_id = self.playlist_tree.item(selected_item, "tags")[0]
        self.add_to_playlist(playlist_id)

    def add_to_playlist(self, playlist_id):
        if self.selected_track_uri:
            sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=[self.selected_track_uri])
            print(f"Added {self.selected_track_uri} to playlist {playlist_id}.")

def startTkinter():
    app = MultiPageApp()
    app.mainloop()

if __name__ == "__main__":
    startTkinter()
