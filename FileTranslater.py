import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from googletrans import Translator, LANGUAGES
import os
import threading
from datetime import datetime, timedelta
import configparser

# Global variables for valid users (replace with your actual user data)
VALID_USERS = {
    "admin-test": {
        "LicenseKey": "77E07E34-FF7F-4798-8668-D65DC184559E",
        "ExpiryDate": datetime(2024, 7, 7)
    },
    "admin-trial": {
        "LicenseKey": "EC951F28-EA8C-45A6-82C1-993212412F63",
        "ExpiryDate": datetime(2024, 7, 15)
    },
    "admin-v1": {
        "LicenseKey": "B1E3F27D-3F44-43BC-8C99-3B7E593E283C",
        "ExpiryDate": datetime(2024, 8, 30)
    },
    "admin-v5": {
        "LicenseKey": "EDAEAFDB-82AF-48F2-BBF0-5EFF7AA8A612",
        "ExpiryDate": datetime(2024, 12, 30)
    },
    "admin-lifetime": {
        "LicenseKey": "5F8D59A4-70DE-4AC4-886B-2FDB4A2C55EA",
        "ExpiryDate": datetime(2555, 12, 30)
    }
}

# Function to validate login credentials
def validate_login():
    username = username_var.get()
    license_key = license_key_var.get()

    if username in VALID_USERS and license_key == VALID_USERS[username]["LicenseKey"]:
        if datetime.now() < VALID_USERS[username]["ExpiryDate"]:
            messagebox.showinfo("Login Successful", "Welcome to the Translation Dashboard!")
            if remember_var.get():
                save_credentials(username, license_key)
            show_dashboard(username)
        else:
            messagebox.showerror("License Expired", "Your license key has expired. Please contact support.")
    else:
        messagebox.showerror("Login Failed", "Invalid username or license key. Please try again.")

# Function to save username and license key to config file
def save_credentials(username, license_key):
    config = configparser.ConfigParser()
    config['Credentials'] = {'Username': username, 'LicenseKey': license_key}

    # Save to config file
    with open('credentials.ini', 'w') as configfile:
        config.write(configfile)

# Function to load saved credentials (if any)
def load_saved_credentials():
    if os.path.exists('credentials.ini'):
        config = configparser.ConfigParser()
        config.read('credentials.ini')
        username = config.get('Credentials', 'Username')
        license_key = config.get('Credentials', 'LicenseKey')
        username_var.set(username)
        license_key_var.set(license_key)
        remember_var.set(True)

# Function to display the translation dashboard
def show_dashboard(username):
    login_frame.grid_forget()  # Hide the login frame
    main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)  # Show the main dashboard frame
    
    # Calculate remaining days until license expiration
    remaining_days = (VALID_USERS[username]["ExpiryDate"] - datetime.now()).days
    
    # Update group box title with username and remaining days
    main_frame.config(text=f"Version 1.0.0 | {username} | {remaining_days} days remaining")

# Function to translate file names (running in a separate thread)
def translate_file_names_thread():
    translate_button['state'] = tk.DISABLED  # Disable translate button during translation

    folder_path = folder_path_var.get()
    selected_country = country_var.get().split(' ')[0]  # Get the language code

    if not folder_path:
        messagebox.showerror("Error", "Please select a folder.")
        translate_button['state'] = tk.NORMAL  # Re-enable translate button
        return

    if not selected_country:
        messagebox.showerror("Error", "Please select a country.")
        translate_button['state'] = tk.NORMAL  # Re-enable translate button
        return

    try:
        translator = Translator()
        files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
        num_files = len(files)
        progress_step = 100 / num_files  # Step size for each file

        progress_bar['maximum'] = 100
        progress_bar['value'] = 0

        # Create log folder if it doesn't exist
        log_folder = "C:/Auto Translate Filename"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Create log file path with index_number_of_log and current_datetime
        log_file_path = os.path.join(log_folder, f"{len(files)}_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"Translation Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for index, file_name in enumerate(files, start=1):
                file_path = os.path.join(folder_path, file_name)
                file_name_no_ext, file_ext = os.path.splitext(file_name)
                translated_name = translator.translate(file_name_no_ext, dest=selected_country).text
                new_file_name = translated_name + file_ext
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)

                # Write log entry (original and translated filenames)
                log_file.write(f"Original: {file_name}\nTranslated: {new_file_name}\n\n")

                progress_value = int(index * progress_step)
                progress_bar['value'] = progress_value
                root.update_idletasks()  # Update the GUI to show progress

        messagebox.showinfo("Success", "File names translated successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        progress_bar['value'] = 100  # Ensure progress bar shows complete
        translate_button['state'] = tk.NORMAL  # Enable translate button after completion

# Function to start file name translation
def translate_file_names():
    # Start translation in a separate thread
    thread = threading.Thread(target=translate_file_names_thread)
    thread.start()

# Function to browse folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_var.set(folder_selected)

# Function to filter countries based on typed text
def filter_countries(event, full_country_list):
    typed_text = country_var.get()
    if typed_text == '':
        country_dropdown['values'] = full_country_list
    else:
        filtered_countries = [country for country in full_country_list if typed_text.lower() in country.lower()]
        country_dropdown['values'] = filtered_countries

# Center the tkinter window on the screen
def center_window(window):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    window.geometry(f"+{x}+{y}")

# Create main window
root = tk.Tk()
root.title("Auto Translate Filename - Phekdey PHORN")

# Center the window on the screen
center_window(root)

# Disable window resizing
root.resizable(False, False)

# Create and set variables for username, license key, and remember checkbox
username_var = tk.StringVar()
license_key_var = tk.StringVar()
remember_var = tk.BooleanVar()

# Load saved credentials (if any)
load_saved_credentials()

# Login frame
login_frame = ttk.Frame(root, padding="20")
login_frame.grid(row=0, column=0, padx=10, pady=10)

tk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
username_entry = ttk.Entry(login_frame, textvariable=username_var)
username_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(login_frame, text="License Key:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
license_key_entry = ttk.Entry(login_frame, textvariable=license_key_var, show='*')
license_key_entry.grid(row=1, column=1, padx=10, pady=10)

remember_checkbox = ttk.Checkbutton(login_frame, text="Remember Me", variable=remember_var)
remember_checkbox.grid(row=2, column=0, columnspan=2, pady=10)

login_button = ttk.Button(login_frame, text="Login", command=validate_login)
login_button.grid(row=3, column=0, columnspan=2, pady=20)

# Main frame for translation dashboard
main_frame = ttk.LabelFrame(root, text="Version 1.0.0")

# Calculate remaining days until license expiration (initially set to 0 days)
remaining_days = 0

# Update group box title with remaining days
main_frame.config(text=f" | {remaining_days} days remaining")

tk.Label(main_frame, text="Select Folder:").grid(row=0, column=0, padx=10, pady=10)
folder_path_var = tk.StringVar()
folder_entry = ttk.Entry(main_frame, textvariable=folder_path_var, width=60)
folder_entry.grid(row=0, column=1, padx=10, pady=10)
browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(main_frame, text="Select Country:").grid(row=1, column=0, padx=10, pady=10)

# Create a list of "code full_name"
full_country_list = [f"{code} - {LANGUAGES[code]}" for code in LANGUAGES.keys()]
country_var = tk.StringVar()
country_dropdown = ttk.Combobox(main_frame, values=full_country_list, textvariable=country_var, width=45)
country_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

# Enable typing and searching in the Combobox
country_dropdown.bind('<KeyRelease>', lambda event: filter_countries(event, full_country_list))

translate_button = ttk.Button(main_frame, text="Translate", command=translate_file_names)
translate_button.grid(row=2, column=0, columnspan=3, pady=20)

progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate', length=300)
progress_bar.grid(row=3, column=0, columnspan=3, pady=10)

# Start with showing the login frame
login_frame.grid(row=0, column=0, padx=10, pady=10)

# Start tkinter main loop
root.mainloop()
