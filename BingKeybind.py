import keyboard
import webbrowser
import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import queue

last_used = 0
cooldown = 5
current_hotkey = 'ctrl+shift+1'
hotkey_handler = None

# Create a single hidden root for all dialogs
main_root = tk.Tk()
main_root.withdraw()  # Hide the main root window
main_root.attributes('-topmost', True)

# Create a queue for actions
action_queue = queue.Queue()

def custom_input_dialog(title, prompt, font, parent, default_text=""):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.attributes('-topmost', True)
    dialog.configure(bg="#181818")
    dialog.resizable(False, False)

    label = tk.Label(dialog, text=prompt, font=font, bg="#181818", fg="#00FFCC", padx=20, pady=10)
    label.pack()

    entry_var = tk.StringVar(value=default_text)
    entry = tk.Entry(dialog, textvariable=entry_var, font=font, bg="#222222", fg="#00FFCC", insertbackground="#00FFCC", width=30)
    entry.pack(padx=20, pady=10)
    entry.focus_set()

    result = {"value": None}

    def on_ok():
        result["value"] = entry_var.get()
        dialog.destroy()

    def on_enter(event):
        on_ok()

    entry.bind("<Return>", on_enter)

    ok_btn = tk.Button(dialog, text="OK", command=on_ok, font=font,
                       bg="#222222", fg="#00FFCC", activebackground="#333333", activeforeground="#FFFFFF", padx=10, pady=5)
    ok_btn.pack(pady=(0, 15))

    dialog.grab_set()
    parent.wait_window(dialog)
    return result["value"]

def search_bing_action():
    global last_used
    now = time.time()
    if now - last_used < cooldown:
        messagebox.showinfo("Cooldown", "Please wait before searching again.", parent=main_root)
        return
    last_used = now

    # Use the same pixel font as your info window
    pixel_font = ("Press Start 2P", 16)
    try:
        tk.Label(main_root, font=pixel_font)
    except tk.TclError:
        pixel_font = ("Courier", 18, "bold")

    query = custom_input_dialog("Bing Search", "Enter your Bing search:", pixel_font, main_root)
    if query:
        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)

def change_hotkey_action():
    global current_hotkey, hotkey_handler
    pixel_font = ("Press Start 2P", 16)
    try:
        tk.Label(main_root, font=pixel_font)
    except tk.TclError:
        pixel_font = ("Courier", 18, "bold")

    new_hotkey = custom_input_dialog("Change Hotkey", "Enter new hotkey (e.g. ctrl+shift+2):", pixel_font, main_root)
    if new_hotkey:
        try:
            if hotkey_handler:
                keyboard.remove_hotkey(hotkey_handler)
            hotkey_handler = keyboard.add_hotkey(new_hotkey, lambda: action_queue.put(search_bing_action))
            current_hotkey = new_hotkey
            messagebox.showinfo("Success", f"Hotkey changed to: {new_hotkey}", parent=main_root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set hotkey: {e}", parent=main_root)

# These functions are called by keyboard (in a background thread)
def search_bing():
    action_queue.put(search_bing_action)

def change_hotkey():
    action_queue.put(change_hotkey_action)

# Register hotkeys
hotkey_handler = keyboard.add_hotkey(current_hotkey, search_bing)
keyboard.add_hotkey('ctrl+shift+s', change_hotkey)

def process_queue():
    while not action_queue.empty():
        action = action_queue.get()
        action()
    main_root.after(100, process_queue)

def quit_app(event=None):
    main_root.quit()

# Bind ESC to quit the app
main_root.bind('<Escape>', quit_app)

def show_keybind_window():
    info_win = tk.Toplevel(main_root)
    info_win.title("Keybind Info")
    info_win.attributes('-topmost', True)
    info_win.configure(bg="#181818")  # Even darker background

    # Try to use a pixel font, fallback to Courier if not available
    pixel_font = ("Press Start 2P", 16)
    try:
        tk.Label(info_win, font=pixel_font)  # Try to create with pixel font
    except tk.TclError:
        pixel_font = ("Courier", 18, "bold")

    info_label = tk.Label(
        info_win,
        text=(
            f"Default search hotkey: {current_hotkey}\n"
            "Change it anytime with Ctrl+Shift+S.\n"
            "Press ESC (with any dialog focused) to exit."
        ),
        padx=30, pady=30,
        font=pixel_font,
        bg="#181818", fg="#00FFCC"  # Bright pixel color for text
    )
    info_label.pack()
    tk.Button(
        info_win,
        text="OK",
        command=info_win.destroy,
        font=pixel_font,
        bg="#222222", fg="#00FFCC", activebackground="#333333", activeforeground="#FFFFFF",
        padx=10, pady=5
    ).pack(pady=(10, 20))

# Call this after creating main_root and before main_root.mainloop()
show_keybind_window()

print("Press ctrl+shift+1 to search Bing.")
print("Press ctrl+shift+s to change the search hotkey.")
print("Press ESC to exit (focus any dialog and press ESC).")

# Start processing the queue and Tkinter main loop
process_queue()
main_root.mainloop()

