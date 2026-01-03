import tkinter as tk
from tkinter import messagebox
import time
import threading
import os
import platform
import datetime
import json
import sys
import keyboard  # pip install keyboard

# VERSION WITH CONFIG FILE AND PIN TO CLOSE
def main():
    # Create window
    root = tk.Tk()
    root.title("Promo Timer")
    
    # Variables
    time_left = 3540  # 59 minutes for countdown
    running = False
    fullscreen_mode = True
    activation_time = None
    waiting_for_schedule = False
    pin_code = "1234"  # Default PIN to close app
    pin_attempts = 0
    max_pin_attempts = 3
    
    # Try to read config from file
    config_file = "timer_config.json"
    default_hour = 13  # 1 PM
    default_minute = 30
    default_second = 0
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                SCHEDULED_HOUR = config.get('hour', default_hour)
                SCHEDULED_MINUTE = config.get('minute', default_minute)
                SCHEDULED_SECOND = config.get('second', default_second)
                pin_code = str(config.get('pin', pin_code))  # Read PIN from config
        else:
            # Create default config file
            config = {
                'hour': default_hour,
                'minute': default_minute,
                'second': default_second,
                'pin': pin_code,
                'note': 'Schedule time in 24-hour format. hour: 0-23, minute: 0-59, second: 0-59'
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            SCHEDULED_HOUR = default_hour
            SCHEDULED_MINUTE = default_minute
            SCHEDULED_SECOND = default_second
            
    except Exception as e:
        print(f"Error reading config: {e}")
        SCHEDULED_HOUR = default_hour
        SCHEDULED_MINUTE = default_minute
        SCHEDULED_SECOND = default_second
    
    # Calculate activation time for today
    today = datetime.datetime.now()
    activation_time = datetime.datetime(
        today.year, today.month, today.day,
        SCHEDULED_HOUR, SCHEDULED_MINUTE, SCHEDULED_SECOND
    )
    
    # If scheduled time has already passed today, schedule for tomorrow
    if activation_time < today:
        activation_time += datetime.timedelta(days=1)
    
    # Global variable to track PIN input
    current_pin_input = ""
    pin_window = None
    
    # Function to show PIN entry dialog
    def show_pin_dialog():
        nonlocal pin_window, current_pin_input, pin_attempts
        
        if pin_window and pin_window.winfo_exists():
            pin_window.destroy()
        
        pin_window = tk.Toplevel(root)
        pin_window.title("Enter PIN to Close")
        pin_window.geometry("300x200")
        pin_window.configure(bg='#2c3e50')
        pin_window.attributes('-topmost', True)
        pin_window.resizable(False, False)
        pin_window.grab_set()
        
        # Center the window
        pin_window.update_idletasks()
        x = (root.winfo_screenwidth() - 300) // 2
        y = (root.winfo_screenheight() - 200) // 2
        pin_window.geometry(f"300x200+{x}+{y}")
        
        # Title
        tk.Label(
            pin_window,
            text="ENTER PIN TO CLOSE",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(pady=10)
        
        # PIN display
        pin_display = tk.Label(
            pin_window,
            text="",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#34495e',
            width=10,
            height=2
        )
        pin_display.pack(pady=10)
        
        # Status label
        status_label = tk.Label(
            pin_window,
            text=f"Attempts remaining: {max_pin_attempts - pin_attempts}",
            font=('Arial', 10),
            fg='white',
            bg='#2c3e50'
        )
        status_label.pack(pady=5)
        
        # Number pad frame
        numpad_frame = tk.Frame(pin_window, bg='#2c3e50')
        numpad_frame.pack(pady=10)
        
        # Function to handle number button click
        def add_digit(digit):
            nonlocal current_pin_input
            if len(current_pin_input) < 4:
                current_pin_input += str(digit)
                pin_display.config(text="*" * len(current_pin_input))
        
        # Function to clear PIN
        def clear_pin():
            nonlocal current_pin_input
            current_pin_input = ""
            pin_display.config(text="")
        
        # Function to submit PIN
        def submit_pin():
            nonlocal current_pin_input, pin_attempts
            if current_pin_input == pin_code:
                # Correct PIN - close app
                pin_window.destroy()
                root.quit()
            else:
                # Wrong PIN
                pin_attempts += 1
                current_pin_input = ""
                pin_display.config(text="")
                
                if pin_attempts >= max_pin_attempts:
                    status_label.config(
                        text="Too many attempts! App will continue.",
                        fg='red'
                    )
                    pin_window.after(2000, pin_window.destroy)
                else:
                    status_label.config(
                        text=f"Wrong PIN! Attempts remaining: {max_pin_attempts - pin_attempts}",
                        fg='red'
                    )
                    pin_window.after(1000, lambda: status_label.config(
                        text=f"Attempts remaining: {max_pin_attempts - pin_attempts}",
                        fg='white'
                    ))
        
        # Create number buttons (1-9)
        buttons = []
        for i in range(1, 10):
            btn = tk.Button(
                numpad_frame,
                text=str(i),
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#3498db',
                width=3,
                height=1,
                command=lambda x=i: add_digit(x)
            )
            btn.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
            buttons.append(btn)
        
        # Row for 0, Clear, and Submit
        row_frame = tk.Frame(numpad_frame, bg='#2c3e50')
        row_frame.grid(row=3, column=0, columnspan=3, pady=2)
        
        # 0 button
        tk.Button(
            row_frame,
            text="0",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#3498db',
            width=3,
            height=1,
            command=lambda: add_digit(0)
        ).pack(side='left', padx=2)
        
        # Clear button
        tk.Button(
            row_frame,
            text="C",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#e74c3c',
            width=3,
            height=1,
            command=clear_pin
        ).pack(side='left', padx=2)
        
        # Submit button
        tk.Button(
            row_frame,
            text="✓",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2ecc71',
            width=3,
            height=1,
            command=submit_pin
        ).pack(side='left', padx=2)
        
        # Bind keyboard events
        def on_key_press(event):
            if event.char.isdigit():
                add_digit(event.char)
            elif event.keysym == 'BackSpace':
                clear_pin()
            elif event.keysym == 'Return':
                submit_pin()
            elif event.keysym == 'Escape':
                pin_window.destroy()
        
        pin_window.bind('<Key>', on_key_press)
        pin_window.focus_set()
    
    # Function to handle Alt+F4 with PIN requirement
    def handle_close(event=None):
        show_pin_dialog()
        return "break"  # Prevent default close action
    
    # Global hotkey for PIN entry (Ctrl+Shift+P)
    def setup_global_hotkey():
        try:
            # Try to set up global hotkey for PIN entry
            keyboard.add_hotkey('ctrl+shift+p', show_pin_dialog)
            print("Global hotkey set: Ctrl+Shift+P to open PIN dialog")
        except Exception as e:
            print(f"Could not set global hotkey: {e}")
    
    # Setup global hotkey
    setup_global_hotkey()
    
    # Function to calculate time until activation
    def get_time_until_activation():
        now = datetime.datetime.now()
        if activation_time > now:
            diff = activation_time - now
            total_seconds = int(diff.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return hours, minutes, seconds
        return 0, 0, 0  # Time has arrived
    
    # Check if it's time to activate
    def check_schedule():
        nonlocal waiting_for_schedule
        hours, minutes, seconds = get_time_until_activation()
        
        if hours == 0 and minutes == 0 and seconds == 0:
            # Time has arrived!
            waiting_for_schedule = False
            root.after(0, show_promo_screen)
        else:
            # Still waiting
            root.after(1000, check_schedule)
    
    # Show waiting screen
    def show_waiting_screen():
        nonlocal waiting_for_schedule
        waiting_for_schedule = True
        
        # Make fullscreen
        root.attributes('-fullscreen', True)
        root.config(bg='black')
        
        # Override close protocol
        root.protocol("WM_DELETE_WINDOW", handle_close)
        
        # Block keys
        def block_keys(event=None):
            return "break"
        
        root.bind('<Alt-Tab>', block_keys)
        root.bind('<Alt_L>', block_keys)
        root.bind('<Alt_R>', block_keys)
        root.bind('<Escape>', block_keys)
        root.bind('<Control-Escape>', block_keys)
        root.bind('<Win_L>', block_keys)
        root.bind('<Win_R>', block_keys)
        root.bind('<Alt-F4>', handle_close)
        
        # Keep window on top
        root.attributes('-topmost', True)
        root.focus_force()
        
        # Create waiting screen
        for widget in root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(root, bg='black')
        frame.pack(expand=True, fill='both')
        
        # Title
        tk.Label(
            frame,
            text="SCHEDULED PROMO",
            font=('Arial', 60, 'bold'),
            fg='white',
            bg='black'
        ).pack(pady=(100, 20))
        
        # Scheduled time
        scheduled_str = activation_time.strftime("%I:%M %p")
        tk.Label(
            frame,
            text=f"Promo starts at: {scheduled_str}",
            font=('Arial', 36),
            fg='yellow',
            bg='black'
        ).pack(pady=(0, 50))
        
        # Countdown label
        countdown_label = tk.Label(
            frame,
            text="",
            font=('Arial', 48, 'bold'),
            fg='#00FF00',
            bg='black'
        )
        countdown_label.pack(pady=(0, 30))
        
        # Current time
        current_label = tk.Label(
            frame,
            text="",
            font=('Arial', 24),
            fg='white',
            bg='black'
        )
        current_label.pack(pady=(0, 100))
        
        # PIN info (hidden by default, shown on Ctrl+Shift+P)
        pin_info = tk.Label(
            frame,
            text="Press Ctrl+Shift+P to enter PIN and close app",
            font=('Arial', 10),
            fg='#888888',
            bg='black'
        )
        pin_info.pack(side='bottom', pady=5)
        
        # Update countdown function
        def update_countdown():
            if waiting_for_schedule:
                hours, minutes, seconds = get_time_until_activation()
                
                if hours > 0:
                    countdown_label.config(
                        text=f"Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}",
                        fg='#00FF00' if hours > 1 else '#FF9900'
                    )
                else:
                    countdown_label.config(
                        text=f"Time remaining: {minutes:02d}:{seconds:02d}",
                        fg='#00FF00' if minutes > 5 else '#FF9900'
                    )
                
                # Update current time
                now = datetime.datetime.now()
                current_label.config(text=f"Current time: {now.strftime('%I:%M:%S %p')}")
                
                root.after(1000, update_countdown)
        
        # Start updating countdown
        update_countdown()
        
        # Message
        tk.Label(
            frame,
            text="Promo will start automatically when time arrives",
            font=('Arial', 18),
            fg='#888888',
            bg='black'
        ).pack(side='bottom', pady=30)
        
        # Start checking schedule
        check_schedule()
    
    # Show promo screen
    def show_promo_screen():
        nonlocal fullscreen_mode
        fullscreen_mode = True
        
        # Clear window
        for widget in root.winfo_children():
            widget.destroy()
        
        # Make fullscreen
        root.attributes('-fullscreen', True)
        root.config(bg='black')
        
        # Override close protocol
        root.protocol("WM_DELETE_WINDOW", handle_close)
        
        # Block keys
        def block_keys(event=None):
            return "break"
        
        root.bind('<Alt-Tab>', block_keys)
        root.bind('<Alt_L>', block_keys)
        root.bind('<Alt_R>', block_keys)
        root.bind('<Escape>', block_keys)
        root.bind('<Control-Escape>', block_keys)
        root.bind('<Win_L>', block_keys)
        root.bind('<Win_R>', block_keys)
        root.bind('<Alt-F4>', handle_close)
        
        # Keep window on top
        def keep_on_top():
            if fullscreen_mode:
                root.attributes('-topmost', True)
                root.focus_force()
            root.after(1000, keep_on_top)
        
        keep_on_top()
        
        # Create frame
        frame = tk.Frame(root, bg='black')
        frame.pack(expand=True, fill='both')
        
        # 1. PROMO TIME text
        label1 = tk.Label(
            frame,
            text="PROMO TIME",
            font=('Arial', 72, 'bold'),
            fg='white',
            bg='black'
        )
        label1.pack(pady=100)
        
        # 2. Timer display
        timer_label = tk.Label(
            frame,
            text="59:00",
            font=('Arial', 120, 'bold'),
            fg='red',
            bg='black'
        )
        timer_label.pack(pady=50)
        
        # 3. START button
        def start_countdown():
            nonlocal fullscreen_mode
            fullscreen_mode = False
            
            # Remove fullscreen
            root.attributes('-fullscreen', False)
            root.attributes('-topmost', False)
            
            # Allow normal close now (but still require PIN)
            root.protocol("WM_DELETE_WINDOW", handle_close)
            
            # Remove keyboard blocking for normal window (except Alt+F4)
            root.unbind('<Alt-Tab>')
            root.unbind('<Alt_L>')
            root.unbind('<Alt_R>')
            root.unbind('<Escape>')
            root.unbind('<Control-Escape>')
            root.unbind('<Win_L>')
            root.unbind('<Win_R>')
            root.bind('<Alt-F4>', handle_close)  # Keep Alt+F4 blocked
            
            # Set window size
            root.geometry("900x500")
            
            # Center window
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - 900) // 2
            y = (screen_height - 500) // 2
            root.geometry(f"900x500+{x}+{y}")
            
            # Clear window
            for widget in root.winfo_children():
                widget.destroy()
            
            # Create countdown screen
            create_countdown_screen()
        
        # Create START button
        start_button = tk.Button(
            frame,
            text="START NOW",
            font=('Arial', 36, 'bold'),
            fg='white',
            bg='#00AA00',
            activeforeground='white',
            activebackground='#008800',
            command=start_countdown,
            padx=40,
            pady=15,
            cursor='hand2',
            relief='flat'
        )
        start_button.pack(pady=50)
        
        # Add hover effect
        def on_enter(e):
            start_button.config(bg='#00CC00')
        
        def on_leave(e):
            start_button.config(bg='#00AA00')
        
        start_button.bind("<Enter>", on_enter)
        start_button.bind("<Leave>", on_leave)
        
        # PIN info
        tk.Label(
            frame,
            text="Press Ctrl+Shift+P to enter PIN and close app",
            font=('Arial', 10),
            fg='#888888',
            bg='black'
        ).pack(side='bottom', pady=5)
        
        # Click START NOW message
        tk.Label(
            frame,
            text="Click START NOW to begin 59-minute countdown",
            font=('Arial', 14),
            fg='#888888',
            bg='black'
        ).pack(side='bottom', pady=20)
        
        # Show message that schedule time has arrived
        root.after(1000, lambda: show_popup("Schedule time has arrived! Click START NOW to begin.", "#00AA00", 3000))
    
    def show_popup(message, color, duration=5000):
        """Show a popup message"""
        screen_width = root.winfo_screenwidth()
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        
        # Position at top center
        popup.geometry(f"400x80+{(screen_width-400)//2}+20")
        
        label = tk.Label(
            popup,
            text=message,
            font=('Arial', 12, 'bold'),
            fg='white',
            bg=color,
            padx=20,
            pady=15,
            wraplength=360,
            justify='center'
        )
        label.pack(fill='both', expand=True)
        
        # Auto close after duration
        popup.after(duration, popup.destroy)
    
    # Create countdown screen (after clicking START)
    def create_countdown_screen():
        root.config(bg='black')
        
        # PIN info frame (top right)
        pin_frame = tk.Frame(root, bg='black')
        pin_frame.pack(anchor='ne', padx=10, pady=10)
        
        tk.Label(
            pin_frame,
            text="Ctrl+Shift+P to enter PIN",
            font=('Arial', 10),
            fg='#888888',
            bg='black'
        ).pack()
        
        # New frame
        new_frame = tk.Frame(root, bg='black')
        new_frame.pack(expand=True, fill='both')
        
        # Countdown timer label
        countdown_label = tk.Label(
            new_frame,
            text="59:00",
            font=('Arial', 100, 'bold'),
            fg='red',
            bg='black'
        )
        countdown_label.pack(expand=True)
        
        # Status label
        status_label = tk.Label(
            new_frame,
            text="Countdown Active - 59 minutes remaining",
            font=('Arial', 20),
            fg='white',
            bg='black'
        )
        status_label.pack(pady=20)
        
        # Info label
        info_label = tk.Label(
            new_frame,
            text="Notifications will appear at 5 minutes and 1 minute",
            font=('Arial', 12),
            fg='#888888',
            bg='black'
        )
        info_label.pack(pady=10)
        
        # Start countdown in thread
        def run_timer():
            nonlocal time_left, running
            running = True
            five_min_shown = False
            one_min_shown = False
            
            while running and time_left > 0:
                # Calculate time
                mins = time_left // 60
                secs = time_left % 60
                
                # Update display
                root.after(0, lambda t=f"{mins:02d}:{secs:02d}": countdown_label.config(text=t))
                
                # Change color for warnings
                if time_left <= 300:
                    root.after(0, lambda: countdown_label.config(fg='orange'))
                    root.after(0, lambda: status_label.config(text="Warning: 5 minutes left!", fg='orange'))
                if time_left <= 60:
                    root.after(0, lambda: countdown_label.config(fg='red'))
                    root.after(0, lambda: status_label.config(text="URGENT: 1 minute left!", fg='red'))
                
                # Check for 5 minute warning
                if not five_min_shown and time_left <= 300:
                    five_min_shown = True
                    show_timer_popup("5 MINUTES LEFT!\nTime is running out", "#FF9900")
                
                # Check for 1 minute warning
                if not one_min_shown and time_left <= 60:
                    one_min_shown = True
                    show_timer_popup("PLEASE LOGOUT YOUR ACCOUNTS NOW!\n1 MINUTE LEFT!", "#FF4444")
                
                # Wait 1 second
                time.sleep(1)
                time_left -= 1
            
            # Time's up
            if time_left <= 0:
                root.after(0, time_up)
        
        def show_timer_popup(message, color):
            screen_width = root.winfo_screenwidth()
            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.attributes('-topmost', True)
            
            # Position at top right
            popup.geometry(f"350x100+{screen_width-370}+20")
            
            # Set text color based on background
            text_color = 'black' if color == "#FF9900" else 'white'
            
            label = tk.Label(
                popup,
                text=message,
                font=('Arial', 12, 'bold'),
                fg=text_color,
                bg=color,
                padx=20,
                pady=15,
                wraplength=300,
                justify='center'
            )
            label.pack(fill='both', expand=True)
            
            # Auto close after 5 seconds
            popup.after(5000, popup.destroy)
        
        def time_up():
            nonlocal running
            running = False
            countdown_label.config(text="00:00", fg='red')
            status_label.config(text="TIME'S UP! Shutting down...", fg='red')
            
            # Create shutdown warning
            warning = tk.Toplevel(root)
            warning.attributes('-fullscreen', True)
            warning.attributes('-topmost', True)
            warning.config(bg='black')
            
            # Make warning window block keys too
            warning.bind('<Alt-Tab>', lambda e: "break")
            warning.bind('<Escape>', lambda e: "break")
            warning.bind('<Alt-F4>', lambda e: "break")
            
            label = tk.Label(
                warning,
                text="TIME'S UP!\nComputer will shutdown in 10 seconds...",
                font=('Arial', 48, 'bold'),
                fg='red',
                bg='black',
                justify='center'
            )
            label.pack(expand=True)
            
            # Warning message
            tk.Label(
                warning,
                text="SAVE ALL WORK NOW!",
                font=('Arial', 28, 'bold'),
                fg='yellow',
                bg='black'
            ).pack(pady=20)
            
            # Countdown function
            def countdown(seconds):
                if seconds > 0 and warning.winfo_exists():
                    label.config(text=f"TIME'S UP!\nComputer will shutdown in {seconds} seconds...")
                    warning.after(1000, countdown, seconds-1)
                elif warning.winfo_exists():
                    shutdown_computer()
            
            # Start countdown
            countdown(10)
        
        def shutdown_computer():
            system = platform.system()
            try:
                if system == "Windows":
                    os.system("shutdown /s /t 1")
                elif system == "Linux":
                    os.system("shutdown -h now")
                elif system == "Darwin":
                    os.system("sudo shutdown -h now")
            except:
                # If shutdown fails, show error
                error = tk.Toplevel(root)
                error.title("Error")
                error.geometry("400x200")
                tk.Label(
                    error,
                    text="Shutdown failed!\nPlease shutdown manually.",
                    font=('Arial', 16),
                    fg='red'
                ).pack(expand=True)
                tk.Button(
                    error,
                    text="OK",
                    command=lambda: [error.destroy(), root.quit()],
                    font=('Arial', 14)
                ).pack(pady=20)
            else:
                root.quit()
        
        # Start timer thread
        timer_thread = threading.Thread(target=run_timer, daemon=True)
        timer_thread.start()
    
    # Console message
    print("=" * 60)
    print("Promo Timer with Config File and PIN Protection")
    print("=" * 60)
    print(f"Schedule read from: {config_file}")
    print(f"Scheduled activation time: {activation_time.strftime('%I:%M %p')}")
    print(f"Current time: {datetime.datetime.now().strftime('%I:%M:%S %p')}")
    print(f"PIN to close app: {pin_code}")
    print("Press Ctrl+Shift+P anytime to enter PIN and close app")
    print("=" * 60)
    
    # Calculate time until activation
    hours, minutes, seconds = get_time_until_activation()
    if hours > 0 or minutes > 0 or seconds > 0:
        print(f"Waiting time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print("Showing waiting screen...")
        show_waiting_screen()
    else:
        print("Scheduled time has arrived!")
        print("Showing promo screen...")
        show_promo_screen()
    
    # Run application
    root.mainloop()

if __name__ == "__main__":
    # First install required package if not installed
    try:
        import keyboard
    except ImportError:
        print("Installing required package: keyboard")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
        import keyboard
    
    main()
