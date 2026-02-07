import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import time
from ctypes import windll, Structure, c_long, byref
import tkinter as tk
from .engine import AIEngine
from .skills.productivity import ProductivityManager
from tkcalendar import Calendar
from datetime import datetime

# --- Theme Configuration ---
THEME = {
    "bg_main": "#1e1e2e",       # Deep dark blue/gray
    "bg_secondary": "#252538",  # Slightly lighter container
    "accent": "#89b4fa",        # Soft Blue
    "accent_hover": "#b4befe",  # Lighter Blue
    "text": "#cdd6f4",          # Off-white
    "text_dark": "#181825",     # Dark text for light backgrounds
    "border": "#45475a",
    "success": "#a6e3a1",       # Green
    "warning": "#f9e2af",       # Yellow
    "error": "#f38ba8"          # Red
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Logic for system tray icon creation
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

class DesktopSidebar(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.productivity = ProductivityManager()
        self.engine = AIEngine(self.productivity)
        
        # Configuration
        self.sidebar_width = 800  # Wide dashboard layout
        self.animation_speed = 0.02 # Seconds per step
        self.animation_step = 20    # Pixels per step
        self.is_open = False
        
        self.configure(fg_color=THEME["bg_main"])
        
        # Hide initial window and remove decorations
        self.overrideredirect(True) # Frameless
        
        # Position it offscreen immediately or correctly to prevent default flash
        w, h, x_offset, y_offset = self.get_rightmost_monitor_geometry()
        target_x = (x_offset + w) - self.sidebar_width
        self.geometry(f"{self.sidebar_width}x{h}+{target_x}+{y_offset}")
        
        self.attributes("-topmost", True) # Always on top
        self.withdraw() # Start hidden
        
        # Layout Setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Tabview expands
        
        # 1. Header (Title + Move Handle)
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#181825")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        
        self.title_lbl = ctk.CTkLabel(self.header, text="DesktopAI", font=("Montserrat", 16, "bold"), text_color=THEME["accent"])
        self.title_lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.close_btn = ctk.CTkButton(self.header, text="✕", width=30, command=self.slide_out, 
                                       fg_color="transparent", hover_color=THEME["error"], text_color=THEME["text"])
        self.close_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 2. Main Content (Tabs)
        self.tab_view = ctk.CTkTabview(self, fg_color="transparent", 
                                       segmented_button_fg_color=THEME["bg_secondary"],
                                       segmented_button_selected_color=THEME["accent"],
                                       segmented_button_selected_hover_color=THEME["accent_hover"],
                                       segmented_button_unselected_color=THEME["bg_main"],
                                       segmented_button_unselected_hover_color=THEME["bg_secondary"],
                                       text_color=THEME["text"])
                                       
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=5)
        self.tab_chat = self.tab_view.add("Chat")
        self.tab_tools = self.tab_view.add("Tools")
        self.tab_settings = self.tab_view.add("Settings")
        
        # --- CHAT TAB ---
        self.setup_chat_tab()
        
        # --- TOOLS TAB ---
        self.setup_tools_tab()

        # --- SETTINGS TAB ---
        self.config_settings_tab()

        # Initialize Tray Icon
        self.setup_tray()
        
        # Start Edge Listener
        threading.Thread(target=self.edge_listener, daemon=True).start()

    def setup_chat_tab(self):
        self.tab_chat.grid_columnconfigure(0, weight=1)
        self.tab_chat.grid_rowconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkScrollableFrame(self.tab_chat, fg_color="transparent")
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.input_frame = ctk.CTkFrame(self.tab_chat, height=50, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type command...", 
                                  fg_color=THEME["bg_secondary"], border_color=THEME["border"], text_color=THEME["text"])
        self.entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.entry.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="➤", width=40, command=self.send_message, 
                                      fg_color=THEME["accent"], hover_color=THEME["accent_hover"], text_color=THEME["text_dark"])
        self.send_btn.grid(row=0, column=1, padx=5)
        
        self.add_message("AI", "System Ready.")

    def setup_tools_tab(self):
        # Tools layout - Sub-tabs or Switcher
        self.tab_tools.grid_columnconfigure(0, weight=1)
        self.tab_tools.grid_rowconfigure(1, weight=1)

        self.tool_type = ctk.CTkSegmentedButton(self.tab_tools, values=["Calendar", "Tasks", "Notes"], command=self.switch_tool_view,
                                                selected_color=THEME["accent"], selected_hover_color=THEME["accent_hover"])
        self.tool_type.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.tool_type.set("Calendar")

        # Container for tool views
        self.tools_container = ctk.CTkFrame(self.tab_tools, fg_color="transparent")
        self.tools_container.grid(row=1, column=0, sticky="nsew")
        self.tools_container.grid_columnconfigure(0, weight=1)
        self.tools_container.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.init_calendar_view()
        self.init_tasks_view()
        self.init_notes_view()
        
        # Show default
        self.switch_tool_view("Calendar")

    def init_calendar_view(self):
        # Grid Layout for Dashboard
        self.cal_frame = ctk.CTkFrame(self.tools_container, fg_color="transparent")
        self.cal_frame.grid_columnconfigure(0, weight=1) # Left Col (Calendar + Deadlines)
        self.cal_frame.grid_columnconfigure(1, weight=1) # Right Col (Schedule + Todos)
        self.cal_frame.grid_rowconfigure(0, weight=1)

        # === LEFT COLUMN ===
        left_col = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(15, 7), pady=15)
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(2, weight=1) # expand deadlines

        # 1. Calendar Widget
        cal_container = ctk.CTkFrame(left_col, fg_color=THEME["bg_secondary"], corner_radius=15, border_width=1, border_color=THEME["border"])
        cal_container.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        today = datetime.now()
        self.cal = Calendar(cal_container, selectmode='day', 
                            year=today.year, month=today.month, day=today.day,
                            background=THEME["bg_main"], 
                            foreground=THEME["text"], 
                            headersbackground=THEME["bg_secondary"],
                            headersforeground=THEME["accent"],
                            normalbackground=THEME["bg_secondary"],
                            normalforeground=THEME["text"],
                            weekendbackground=THEME["bg_secondary"],
                            weekendforeground=THEME["text"],
                            othermonthwebackground=THEME["bg_secondary"],
                            othermonthweforeground="#6c7086", 
                            othermonthbackground=THEME["bg_secondary"],
                            selectbackground=THEME["accent"],
                            selectforeground=THEME["text_dark"],
                            bordercolor=THEME["bg_main"],
                            font=("Arial", 10)) 
        
        self.cal.pack(pady=15, padx=15, fill="both", expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_selected)

        # 2. Add Event Button & Form (Global)
        self.add_event_btn = ctk.CTkButton(left_col, text="+ New Event / Task", height=32, 
                                           command=self.toggle_add_event_form, 
                                           fg_color=THEME["accent"], hover_color=THEME["accent_hover"],
                                           text_color=THEME["text_dark"], font=("Arial", 12, "bold"))
        self.add_event_btn.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Inline Add Event Form (Hidden by default)
        self.add_event_frame = ctk.CTkFrame(left_col, fg_color=THEME["bg_secondary"], corner_radius=10)
        self.setup_add_event_form()

        # 3. Upcoming Deadlines
        deadlines_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        deadlines_frame.grid(row=2, column=0, sticky="nsew")
        
        ctk.CTkLabel(deadlines_frame, text="Upcoming Deadlines", font=("Montserrat", 14, "bold"), text_color=THEME["text"], anchor="w").pack(fill="x", pady=(0, 5))
        self.deadlines_list = ctk.CTkScrollableFrame(deadlines_frame, fg_color="transparent", height=150)
        self.deadlines_list.pack(fill="both", expand=True)

        # === RIGHT COLUMN ===
        right_col = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(7, 15), pady=15)
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(1, weight=1) # Schedule expands
        right_col.grid_rowconfigure(3, weight=1) # ToDo expands

        # 4. Schedule Header
        self.schedule_header = ctk.CTkLabel(right_col, text="Schedule", font=("Montserrat", 18, "bold"), text_color=THEME["accent"], anchor="w")
        self.schedule_header.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # 5. Timeline / Schedule (Timed Events)
        self.timeline_list = ctk.CTkScrollableFrame(right_col, fg_color=THEME["bg_secondary"], corner_radius=10)
        self.timeline_list.grid(row=1, column=0, sticky="nsew", pady=(0, 15))

        # 6. To-Do List (Untimed)
        ctk.CTkLabel(right_col, text="To-Do List", font=("Montserrat", 14, "bold"), text_color=THEME["text"], anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.todo_list = ctk.CTkScrollableFrame(right_col, fg_color=THEME["bg_secondary"], corner_radius=10)
        self.todo_list.grid(row=3, column=0, sticky="nsew")

    def setup_add_event_form(self):
        padding_frame = ctk.CTkFrame(self.add_event_frame, fg_color="transparent")
        padding_frame.pack(padx=10, pady=10, fill="x")
        
        self.ae_title = ctk.CTkEntry(padding_frame, placeholder_text="Event Title", fg_color=THEME["bg_main"], border_color=THEME["border"])
        self.ae_title.pack(fill="x", pady=(0, 5))
        
        row1 = ctk.CTkFrame(padding_frame, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        self.ae_time = ctk.CTkEntry(row1, placeholder_text="Start Time (e.g. 14:00)", fg_color=THEME["bg_main"], border_color=THEME["border"])
        self.ae_time.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.ae_end_time = ctk.CTkEntry(row1, placeholder_text="End Time (e.g. 15:00)", fg_color=THEME["bg_main"], border_color=THEME["border"])
        self.ae_end_time.pack(side="right", fill="x", expand=True, padx=(2, 0))
        
        row2 = ctk.CTkFrame(padding_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(8, 0))
        self.ae_reminder = ctk.CTkCheckBox(row2, text="Reminder", text_color=THEME["text"], hover_color=THEME["accent"], fg_color=THEME["accent"])
        self.ae_reminder.pack(side="left")
        self.ae_save_btn = ctk.CTkButton(row2, text="Save", width=60, height=24, command=self.save_event_inline, 
                                         fg_color=THEME["success"], hover_color="#8bd5ca", text_color=THEME["text_dark"])
        self.ae_save_btn.pack(side="right")

    def toggle_add_event_form(self):
        if self.add_event_frame.winfo_manager(): 
            self.add_event_frame.grid_forget()
            self.add_event_btn.configure(text="+ New Event / Task", fg_color=THEME["accent"])
        else:
            self.add_event_btn.grid_forget()
            self.add_event_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
    
    def save_event_inline(self):
        title = self.ae_title.get()
        if not title: return

        date_str = self.cal.get_date()
        try:
             dt = datetime.strptime(date_str, "%m/%d/%y")
             iso_date = dt.strftime("%Y-%m-%d")
        except:
             try:
                 dt = datetime.strptime(date_str, "%Y-%m-%d")
                 iso_date = dt.strftime("%Y-%m-%d")
             except:
                 iso_date = date_str
        
        self.productivity.add_task(
            title, iso_date, 
            self.ae_time.get(), 
            self.ae_end_time.get(), 
            self.ae_reminder.get()
        )
        self.load_day_events(iso_date) # Refresh dashboard
        
        # Reset but keep form or hide? User usually wants to add one. Let's hide to confirm.
        self.ae_title.delete(0, "end")
        self.ae_time.delete(0, "end")
        self.ae_end_time.delete(0, "end")
        self.ae_reminder.deselect()
        
        self.add_event_frame.grid_forget()
        self.add_event_btn.grid(row=1, column=0, sticky="ew", pady=(0, 15))

    def on_date_selected(self, event):
        date_str = self.cal.get_date()
        try:
             dt = datetime.strptime(date_str, "%m/%d/%y")
             iso_date = dt.strftime("%Y-%m-%d")
        except:
             try:
                 dt = datetime.strptime(date_str, "%Y-%m-%d")
                 iso_date = dt.strftime("%Y-%m-%d")
             except:
                 iso_date = date_str # Fallback
        
        # Update Header
        pretty_date = datetime.strptime(iso_date, "%Y-%m-%d").strftime("%A, %B %d")
        self.schedule_header.configure(text=f"Schedule for {pretty_date}")
        
        self.load_calendar_dashboard(iso_date)

    def load_day_events(self, date_str):
        self.load_calendar_dashboard(date_str)

    def load_calendar_dashboard(self, date_str):
        # 1. Clear Lists
        for widget in self.timeline_list.winfo_children(): widget.destroy()
        for widget in self.todo_list.winfo_children(): widget.destroy()
        for widget in self.deadlines_list.winfo_children(): widget.destroy()

        # 2. Get Data
        day_tasks = self.productivity.get_tasks_for_date(date_str)
        upcoming = self.productivity.get_upcoming_tasks(10)

        # 3. Populate Schedule (Timed) & Todos (Untimed)
        timed = [t for t in day_tasks if t.get("time")]
        untimed = [t for t in day_tasks if not t.get("time")]
        
        timed.sort(key=lambda x: x["time"]) # Sort by time
        
        for task in timed:
            self.create_dashboard_card(self.timeline_list, task, is_timed=True)
            
        for task in untimed:
            self.create_dashboard_card(self.todo_list, task, is_timed=False)
            
        if not timed:
            ctk.CTkLabel(self.timeline_list, text="No scheduled events.", text_color="gray").pack(pady=10)
        if not untimed:
            ctk.CTkLabel(self.todo_list, text="No pending tasks.", text_color="gray").pack(pady=10)

        # 4. Populate Deadlines
        for task in upcoming:
            self.create_dashboard_card(self.deadlines_list, task, is_timed=bool(task.get("time")), show_date=True)

    def create_dashboard_card(self, parent, task, is_timed=False, show_date=False):
        row = ctk.CTkFrame(parent, height=40, fg_color=THEME["bg_main"] if parent == self.timeline_list else THEME["bg_secondary"], corner_radius=8)
        row.pack(fill="x", pady=4, padx=5)
        
        # Checkbox
        status_var = ctk.BooleanVar(value=task["completed"])
        chk = ctk.CTkCheckBox(row, text="", variable=status_var, width=20, corner_radius=10, 
                              fg_color=THEME["accent"], hover_color=THEME["accent_hover"], border_color=THEME["border"],
                               command=lambda: self.productivity.toggle_task(task["id"]))
        chk.pack(side="left", padx=(10, 5))

        # Content
        details_frame = ctk.CTkFrame(row, fg_color="transparent")
        details_frame.pack(side="left", fill="x", expand=True, pady=5)
        
        title_text = task["title"]
        title_lbl = ctk.CTkLabel(details_frame, text=title_text, anchor="w", font=("Arial", 12, "bold"), text_color=THEME["text"])
        title_lbl.pack(fill="x")
        
        meta = []
        if task.get("category") == "Deadline": meta.append("⚠️ Deadline")
        if show_date: meta.append(f"📅 {task['date']}")
        if is_timed and task.get("time"):
            time_str = f"{task['time']}"
            if task.get("end_time"): time_str += f" - {task['end_time']}"
            meta.append(f"🕒 {time_str}")
        
        if meta:
             ctk.CTkLabel(details_frame, text="  ".join(meta), anchor="w", font=("Arial", 10), text_color="#a6adc8").pack(fill="x")

        # Delete (Tiny x)
        ctk.CTkButton(row, text="×", width=20, height=20, fg_color="transparent", hover_color=THEME["error"], 
                      text_color=THEME["text"], command=lambda: [self.productivity.delete_task(task["id"]), row.destroy()]).pack(side="right", padx=5)

    def init_tasks_view(self):
        self.tasks_frame = ctk.CTkFrame(self.tools_container, fg_color="transparent")
        self.tasks_frame.grid_columnconfigure(0, weight=1)
        self.tasks_frame.grid_rowconfigure(1, weight=1)
        
        # Input Area
        input_area = ctk.CTkFrame(self.tasks_frame, height=40, fg_color="transparent")
        input_area.pack(fill="x", padx=5, pady=5)
        
        self.task_entry = ctk.CTkEntry(input_area, placeholder_text="New Task...", fg_color=THEME["bg_secondary"], border_color=THEME["border"])
        self.task_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.task_entry.bind("<Return>", self.add_task_ui)
        
        add_btn = ctk.CTkButton(input_area, text="+", width=30, command=self.add_task_ui, fg_color=THEME["accent"], text_color=THEME["text_dark"])
        add_btn.pack(side="right", padx=5)
        
        # Task List
        self.task_list_frame = ctk.CTkScrollableFrame(self.tasks_frame, fg_color="transparent")
        self.task_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.refresh_task_list()

    def add_task_ui(self, event=None):
        text = self.task_entry.get()
        if not text: return
        today = datetime.now().strftime("%Y-%m-%d")
        self.productivity.add_task(text, today)
        self.task_entry.delete(0, "end")
        self.refresh_task_list()

    def refresh_task_list(self):
        for widget in self.task_list_frame.winfo_children(): widget.destroy()
        tasks = self.productivity.get_all_tasks()
        tasks.sort(key=lambda x: x["completed"])
        for task in tasks:
            self.create_dashboard_card(self.task_list_frame, task, is_timed=bool(task.get("time")), show_date=True)

    def init_notes_view(self):
        self.notes_frame = ctk.CTkFrame(self.tools_container, fg_color="transparent")
        self.notes_frame.grid_columnconfigure(0, weight=1)
        self.notes_frame.grid_rowconfigure(0, weight=1)
        
        self.notes_text = ctk.CTkTextbox(self.notes_frame, font=("Arial", 12), fg_color=THEME["bg_secondary"], text_color=THEME["text"])
        self.notes_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        content = self.productivity.get_scratchpad()
        self.notes_text.insert("1.0", content)
        
        save_btn = ctk.CTkButton(self.notes_frame, text="Save Notes", command=self.save_notes_ui, fg_color=THEME["accent"], text_color=THEME["text_dark"])
        save_btn.grid(row=1, column=0, pady=(0, 10))

    def save_notes_ui(self):
        content = self.notes_text.get("1.0", "end-1c")
        self.productivity.save_scratchpad(content)

    def switch_tool_view(self, view_name):
        for frame in [self.cal_frame, self.tasks_frame, self.notes_frame]:
            frame.forget()
        if view_name == "Calendar":
            self.cal_frame.pack(fill="both", expand=True)
            self.on_date_selected(None) # Refresh
        elif view_name == "Tasks":
            self.tasks_frame.pack(fill="both", expand=True)
        elif view_name == "Notes":
            self.notes_frame.pack(fill="both", expand=True)

    def get_rightmost_monitor_geometry(self):
        try:
            import ctypes
            from ctypes import windll, byref, Structure, c_long, c_int, POINTER, sizeof
            from ctypes.wintypes import RECT, DWORD

            class MONITORINFO(Structure):
                _fields_ = [
                    ("cbSize", DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", DWORD)
                ]

            monitors = []
            
            def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                try:
                    mi = MONITORINFO()
                    mi.cbSize = sizeof(MONITORINFO)
                    if windll.user32.GetMonitorInfoW(hMonitor, byref(mi)):
                        monitors.append((mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom))
                    else:
                        r = lprcMonitor.contents
                        monitors.append((r.left, r.top, r.right, r.bottom))
                    return 1
                except:
                    return 0
            
            MonitorEnumProc = ctypes.WINFUNCTYPE(c_int, c_long, c_long, POINTER(RECT), c_long)
            cb = MonitorEnumProc(_callback)
            windll.user32.EnumDisplayMonitors(0, 0, cb, 0)
            
            if not monitors:
                rect = RECT()
                windll.user32.SystemParametersInfoW(48, 0, byref(rect), 0)
                return rect.right - rect.left, rect.bottom - rect.top, rect.left, rect.top
            
            monitors.sort(key=lambda m: m[2], reverse=True)
            best_mon = monitors[0] 
            
            l, t, r, b = best_mon
            width = r - l
            height = b - t 
            return width, height, l, t
        except Exception as e:
            return self.winfo_screenwidth(), self.winfo_screenheight() - 48, 0, 0

    def change_music_mode(self, choice):
        self.engine.set_music_mode(choice)

    def toggle_panel(self, icon=None, item=None):
        if self.is_open:
            self.slide_out()
        else:
            self.slide_in()

    def slide_in(self):
        w, h, x_offset, y_offset = self.get_rightmost_monitor_geometry()
        target_x = (x_offset + w) - self.sidebar_width
        
        # Start specific handling for animation
        # Always place it on topmost before animating
        self.deiconify() 
        self.attributes("-topmost", True)
        self.lift()
        self.is_open = True
        
        # Start animation from right (off-screen)
        start_x = x_offset + w
        
        def animate(current_x):
            if current_x > target_x:
                new_x = max(current_x - self.animation_step * 2, target_x)
                self.geometry(f"{self.sidebar_width}x{h}+{int(new_x)}+{y_offset}")
                self.after(5, lambda: animate(new_x))
            else:
                # Snap to final
                self.geometry(f"{self.sidebar_width}x{h}+{target_x}+{y_offset}")
                # Auto-focus input
                self.after(100, lambda: self.entry.focus_set())

        animate(start_x)

    def slide_out(self):
        self.is_open = False
        w, h, x_offset, y_offset = self.get_rightmost_monitor_geometry()
        start_x = self.winfo_x()
        target_x = x_offset + w
        
        def animate(current_x):
            if current_x < target_x:
                new_x = min(current_x + self.animation_step * 2, target_x)
                self.geometry(f"{self.sidebar_width}x{h}+{int(new_x)}+{y_offset}")
                self.after(5, lambda: animate(new_x))
            else:
                self.withdraw()

        animate(start_x)

    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.destroy()
        sys.exit()

    def send_message(self, event=None):
        text = self.entry.get()
        if not text: return
        self.entry.delete(0, "end")
        self.add_message("You", text)
        threading.Thread(target=self.process_response, args=(text,), daemon=True).start()

    def process_response(self, text):
        response = self.engine.process_input(text)
        self.add_message("AI", response)
        
        # Refresh UI Trigger
        if "Scheduled event" in response or "Added task" in response:
            # Refresh both calendar dashboard and tasks list
            self.after(0, lambda: self.on_date_selected(None)) 
            self.after(0, self.refresh_task_list)
            
        elif "Note saved" in response:
            self.after(0, self.refresh_notes_view)

    def refresh_notes_view(self):
        # preserve scroll position? For now just reload
        content = self.productivity.get_scratchpad()
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", content)

    def add_message(self, sender, text):
        color = THEME["accent"] if sender == "You" else THEME["bg_secondary"]
        text_color = THEME["text_dark"] if sender == "You" else THEME["text"]
        align = "e" if sender == "You" else "w"
        
        container = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        container.pack(pady=5, padx=5, anchor=align, fill="x")
        
        # Message Bubble
        bubble = ctk.CTkFrame(container, fg_color=color, corner_radius=10)
        bubble.pack(anchor=align, padx=5) # pack inside container to allow alignment
        
        # Text Label 
        lbl = ctk.CTkLabel(bubble, text=text, text_color=text_color, wraplength=int(self.sidebar_width * 0.7), justify="left")
        lbl.pack(padx=10, pady=5)
        
        # Context Menu for Copy
        def show_context_menu(event):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Copy Text", command=lambda: self.copy_to_clipboard(text))
            menu.tk_popup(event.x_root, event.y_root)

        lbl.bind("<Button-3>", show_context_menu)
        bubble.bind("<Button-3>", show_context_menu)
        
        self.chat_display._parent_canvas.yview_moveto(1.0)
        
    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update() # Required to finalize clipboard event

    def config_settings_tab(self):
        self.music_label = ctk.CTkLabel(self.tab_settings, text="Music Source:", anchor="w", text_color=THEME["text"])
        self.music_label.pack(anchor="w", padx=10, pady=(20, 5))
        
        self.music_menu = ctk.CTkOptionMenu(self.tab_settings, values=["Spotify", "YouTube"], command=self.change_music_mode,
                                            fg_color=THEME["bg_secondary"], text_color=THEME["text"], button_color=THEME["accent"], button_hover_color=THEME["accent_hover"])
        self.music_menu.pack(anchor="w", padx=10)
        self.music_menu.set("Spotify")
        
        self.quit_btn = ctk.CTkButton(self.tab_settings, text="Quit Application", fg_color=THEME["error"], hover_color="#eba0ac", text_color=THEME["text_dark"], command=self.quit_app)
        self.quit_btn.pack(side="bottom", pady=20, padx=10, fill="x")

    def setup_tray(self):
        icon_image = create_image(64, 64, 'white', 'blue')
        menu = (
            pystray.MenuItem('DesktopAI', self.toggle_panel, default=True, visible=False),
            pystray.MenuItem('Show/Hide', self.toggle_panel),
            pystray.MenuItem('Quit', self.quit_app)
        )
        self.icon = pystray.Icon("DesktopAI", icon_image, "DesktopAI", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def edge_listener(self):
        class POINT(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]

        hover_start_time = 0
        is_hovering = False
        
        # Buffer variables for auto-close
        leave_start_time = 0
        is_leaving = False
        
        while True:
            try:
                pt = POINT()
                windll.user32.GetCursorPos(byref(pt))
                w, h, x_off, y_off = self.get_rightmost_monitor_geometry()
                
                right_edge_x = x_off + w
                sidebar_left_x = right_edge_x - self.sidebar_width
                
                # 1. Opening Logic
                on_edge = False
                if pt.x >= right_edge_x - 3:
                    on_edge = True
                
                if on_edge and not self.is_open:
                    if not is_hovering:
                        is_hovering = True
                        hover_start_time = time.time()
                    elif time.time() - hover_start_time >= 0.5:
                        self.after(0, self.slide_in)
                        is_hovering = False
                else:
                    is_hovering = False
                
                # 2. Auto-Close Logic
                if self.is_open:
                    # Check if cursor is strictly OUTSIDE the sidebar box
                    # We give a small buffer (e.g. 50px left) so it doesn't close immediately if you slip
                    inside_x = (pt.x >= sidebar_left_x)
                    
                    if not inside_x:
                        if not is_leaving:
                            is_leaving = True
                            leave_start_time = time.time()
                        elif time.time() - leave_start_time >= 0.3: # 300ms delay
                            self.after(0, self.slide_out)
                            is_leaving = False
                    else:
                        is_leaving = False
                    
            except Exception as e:
                pass
            time.sleep(0.1)

if __name__ == "__main__":
    app = DesktopSidebar()
    app.mainloop()
