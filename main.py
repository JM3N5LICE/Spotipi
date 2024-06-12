import tkinter as tk
from PIL import Image, ImageTk
import time

class MultiPageApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.pages = {}
        self.page_order = ["Page1", "Page2", "Page3"]

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

class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page 1: Time Display")
        label.pack()

        self.time_label = tk.Label(self, text="", font=("Helvetica", 48))
        self.time_label.pack()

        self.update_time()

        button = tk.Button(self, text="Go to Page 2", command=lambda: controller.show_page("Page2"))
        button.pack()

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page 2: Music Control")
        label.pack()

        # Load and resize custom icons from the images folder
        self.play_icon = self.load_and_resize_icon("images/play2.png", 50, 50)
        self.pause_icon = self.load_and_resize_icon("images/pause2.png", 50, 50)
        self.skip_icon = self.load_and_resize_icon("images/skip.png", 50, 50)
        self.prev_icon = self.load_and_resize_icon("images/previous.png", 50, 50)

        # Create buttons with custom icons
        button_play = tk.Button(self, image=self.play_icon, command=self.play_music)
        button_play.pack()

        button_pause = tk.Button(self, image=self.pause_icon, command=self.pause_music)
        button_pause.pack()

        button_skip = tk.Button(self, image=self.skip_icon, command=self.skip_music)
        button_skip.pack()

        button_prev = tk.Button(self, image=self.prev_icon, command=self.prev_music)
        button_prev.pack()

    def load_and_resize_icon(self, path, width, height):
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def play_music(self):
        print("Playing music...")

    def pause_music(self):
        print("Pausing music...")

    def skip_music(self):
        print("Skipping to next track...")

    def prev_music(self):
        print("Going to previous track...")

class Page3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page 3: Playlist Selection")
        label.pack()

        self.playlist_label = tk.Label(self, text="Select a playlist:")
        self.playlist_label.pack()

        self.playlist_entry = tk.Entry(self)
        self.playlist_entry.pack()

        self.track_label = tk.Label(self, text="Select a track:")
        self.track_label.pack()

        self.track_entry = tk.Entry(self)
        self.track_entry.pack()

        button_select = tk.Button(self, text="Play Track", command=self.play_selected_track)
        button_select.pack()

    def play_selected_track(self):
        playlist_name = self.playlist_entry.get()
        track_number = self.track_entry.get()
        print(f"Playing track {track_number} from playlist {playlist_name}...")

def startTkinter():
    app = MultiPageApp()
    app.mainloop()
