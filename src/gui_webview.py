import webview
import threading
import sys
import time
import os
import ctypes
import pystray
from PIL import Image, ImageDraw
from ctypes import windll, byref, Structure, c_long, c_int, POINTER, sizeof
from ctypes.wintypes import RECT, DWORD
from .engine import AIEngine
from .skills.productivity import ProductivityManager
from datetime import datetime

# --- Tray Icon Helpers ---
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

class DesktopAIBridge:
    def __init__(self):
        self.productivity = ProductivityManager()
        self.engine = AIEngine(self.productivity)
        self.window = None

    def process_command(self, text):
        return self.engine.process_input(text)

    def get_dashboard_data(self, date_str=None):
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        tasks = self.productivity.get_tasks_for_date(date_str)
        upcoming = self.productivity.get_upcoming_tasks(10)
        return {
            "view_date": date_str,
            "tasks": tasks,
            "upcoming": upcoming
        }

    def toggle_task(self, task_id):
        self.productivity.toggle_task(task_id)
        return True

    def get_music_history(self):
        return self.engine.music.get_history()

    def play_music_history_item(self, index):
        # index is 0-based from UI probably, or let's use 1-based to match engine
        return self.engine.music.play_from_history(int(index) + 1)

    def delete_task(self, task_id):
        self.productivity.delete_task(task_id)
        return True

    def quick_add_task(self, title):
        today = datetime.now().strftime("%Y-%m-%d")
        self.productivity.add_task(title, today)
        return True

    def update_setting(self, key, value):
        if key == "music_source":
            self.engine.set_music_mode(value)
    
    def minimize(self):
        self.window.minimize()

    def hide_window(self):
        slide_out(self.window)

    def quit_app(self):
        global TRAY_ICON
        if TRAY_ICON:
             TRAY_ICON.stop()
        self.window.destroy()
        sys.exit()

# --- Window Management Logic ---

SIDEBAR_WIDTH = 800
ANIMATION_STEP = 50
IS_OPEN = False
TRAY_ICON = None

def get_rightmost_monitor_geometry():
    try:
        monitors = []
        def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = lprcMonitor.contents
            monitors.append((r.left, r.top, r.right, r.bottom))
            return 1

        MonitorEnumProc = ctypes.WINFUNCTYPE(c_int, c_long, c_long, POINTER(RECT), c_long)
        cb = MonitorEnumProc(_callback)
        windll.user32.EnumDisplayMonitors(0, 0, cb, 0)
        
        if not monitors: return 1920, 1080, 0, 0
        
        monitors.sort(key=lambda m: m[2], reverse=True)
        l, t, r, b = monitors[0]
        return (r - l), (b - t), l, t
    except:
        return 1920, 1080, 0, 0

def slide_in(window):
    global IS_OPEN
    if IS_OPEN: return
    
    w, h, x_off, y_off = get_rightmost_monitor_geometry()
    target_x = (x_off + w) - SIDEBAR_WIDTH
    start_x = x_off + w
    
    # Pre-position
    window.resize(SIDEBAR_WIDTH, h)
    window.move(start_x, y_off)
    window.restore() # Show it
    
    # Animate
    current_x = start_x
    while current_x > target_x:
        current_x -= ANIMATION_STEP
        window.move(int(current_x), y_off)
        time.sleep(0.005) # 5ms
    
    window.move(int(target_x), y_off)
    IS_OPEN = True
    
    # Always On Top
    hwnd = windll.user32.FindWindowW(None, "DesktopAI")
    windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3) # HWND_TOPMOST | SWP_NOMOVE | SWP_NOSIZE

def slide_out(window):
    global IS_OPEN
    if not IS_OPEN: return
    
    w, h, x_off, y_off = get_rightmost_monitor_geometry()
    target_x = x_off + w
    current_x = window.x
    
    while current_x < target_x:
        current_x += ANIMATION_STEP
        window.move(int(current_x), y_off)
        time.sleep(0.005)
        
    window.hide()
    IS_OPEN = False

def edge_listener(window):
    class POINT(Structure):
        _fields_ = [("x", c_long), ("y", c_long)]

    hover_start = 0
    is_hovering = False
    
    leave_start = 0
    is_leaving = False
    
    while True:
        try:
            pt = POINT()
            windll.user32.GetCursorPos(byref(pt))
            w, h, x_off, y_off = get_rightmost_monitor_geometry()
            right_edge = x_off + w
            
            # Open Logic
            if pt.x >= right_edge - 3:
                if not is_hovering:
                    is_hovering = True
                    hover_start = time.time()
                elif time.time() - hover_start >= 0.3:
                    if not IS_OPEN: 
                        # Must run on main thread preferably, but pywebview is thread safe-ish
                        # For window moves it's fine
                        slide_in(window)
                    is_hovering = False
            else:
                is_hovering = False
            
            # Close Logic
            if IS_OPEN:
                sidebar_left = right_edge - SIDEBAR_WIDTH
                if pt.x < sidebar_left:
                    if not is_leaving:
                        is_leaving = True
                        leave_start = time.time()
                    elif time.time() - leave_start >= 0.4:
                        slide_out(window)
                        is_leaving = False
                else:
                    is_leaving = False
                    
        except Exception as e:
            print(e)
            pass
        time.sleep(0.1)

def setup_tray(window):
    global TRAY_ICON
    
    def on_quit(icon, item):
        icon.stop()
        window.destroy()
        sys.exit()

    def on_show(icon, item):
        slide_in(window)

    icon_image = create_image(64, 64, 'white', 'blue')
    menu = (
        pystray.MenuItem('Show DesktopAI', on_show, default=True),
        pystray.MenuItem('Quit', on_quit)
    )
    TRAY_ICON = pystray.Icon("DesktopAI", icon_image, "DesktopAI", menu)
    threading.Thread(target=TRAY_ICON.run, daemon=True).start()

def start_app():
    bridge = DesktopAIBridge()
    
    # Path to HTML
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'web/index.html')
    url = f"file:///{html_path.replace(os.sep, '/')}"
    
    # Create Window (Hidden initially)
    window = webview.create_window(
        'DesktopAI', 
        url, 
        width=SIDEBAR_WIDTH, 
        height=1080, 
        frameless=True, 
        easy_drag=False,
        on_top=True
    )
    bridge.window = window
    window.expose(bridge.process_command, bridge.get_dashboard_data, bridge.toggle_task, 
                 bridge.delete_task, bridge.quick_add_task, bridge.update_setting, 
                 bridge.quit_app, bridge.hide_window, bridge.minimize,
                 bridge.get_music_history, bridge.play_music_history_item,
                 bridge.engine.music.delete_history_item, bridge.engine.music.clear_history)
    
    # Initialize Tray
    setup_tray(window)
    
    # Start Listener
    t = threading.Thread(target=edge_listener, args=(window,))
    t.daemon = True
    t.start()
    
    # Start App - PyWebview acts as main loop
    webview.start(debug=False)

if __name__ == "__main__":
    start_app()
