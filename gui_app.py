import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from inference import predict_image  # Assuming the inference function is in inference.py
import re

# Function to classify and organize files
def classify_and_organize_files(source_path, destination_path, mode, organize_by):
    if not os.path.exists(source_path):
        messagebox.showerror("Error", "Source path does not exist.")
        return

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Get the total number of files to process
    total_files = sum(len(files) for _, _, files in os.walk(source_path))
    processed_files = 0

    for root_path, dirs, files in os.walk(source_path):
        for file_name in files:
            file_path = os.path.join(root_path, file_name)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_name)
                if organize_by == "Content":
                    if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp']:
                        category = "image/" + predict_image(file_path)
                    elif ext.lower() in ['.pdf', '.docx', '.ppt', '.txt']:
                        category = "pdfs"
                    elif ext.lower() in ['.csv', '.xlsx']:
                        category = "datasheets"
                    elif ext.lower() in ['.mp4', '.mkv', '.webm']:
                        category = "videos"
                    elif ext.lower() in ['.mp3']:
                        category = "audios"
                    else:
                        category = "others"
                else:
                    if re.match(r".*\.(png|jpg|jpeg|webp|)$", file_path):
                        category = "images"
                    if re.match(r".*\.(pdf|docx|ppt|txt)$", file_path):
                        category = "pdfs"
                    if re.match(r".*\.(csv|xlsx)$", file_path):
                        category = "datasheets"
                    if re.match(r".*\.(mp4|mkv|webm)$", file_path):
                        category = "videos"
                    if re.match(r".*\.(mp3)$", file_path):
                        category = "audios"
                    if re.match(r".*\.(exe|apk|msi)$", file_path):
                        category = "softwares"
                    if re.match(r".*\.(zip)$", file_path):
                        category = "zips"  # Organize by file extension
                    else:
                        category = "others"

                if mode == "Separate by Folders":
                    relative_path = os.path.relpath(root_path, source_path)
                    target_dir = os.path.join(destination_path, category, relative_path)
                    target_path = os.path.join(target_dir, file_name)
                    os.makedirs(target_dir, exist_ok=True)
                else:
                    if category == "images":
                        target_path = os.path.join(file_path, f"{category}_{file_name}")
                    else:
                        target_path = os.path.join(file_path, f"{file_name}-({category})")

                shutil.copy(file_path, target_path)

                # Update progress bar
                processed_files += 1
                progress_var.set((processed_files / total_files) * 100)
                root.update_idletasks()

    messagebox.showinfo("Success", "Files have been organized successfully.")

# Function to browse for source path
def browse_source():
    source_path.set(filedialog.askdirectory())

# Function to browse for destination path
def browse_destination():
    destination_path.set(filedialog.askdirectory())

# Create the main application window
root = tk.Tk()
root.title("File Organizer")
root.geometry("600x400")
root.resizable(False, False)

# Create and place widgets
source_path = tk.StringVar()
destination_path = tk.StringVar()
mode = tk.StringVar(value="Separate by Folders")
organize_by = tk.StringVar(value="Content")
progress_var = tk.DoubleVar()

ttk.Label(root, text="Source Path:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
ttk.Entry(root, textvariable=source_path, width=50).grid(row=0, column=1, padx=10, pady=10)
ttk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2, padx=10, pady=10)

ttk.Label(root, text="Destination Path:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
ttk.Entry(root, textvariable=destination_path, width=50).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2, padx=10, pady=10)

ttk.Label(root, text="Mode:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
ttk.Radiobutton(root, text="Include Class in File Name", variable=mode, value="Include Class in File Name").grid(row=2, column=1, padx=10, pady=10, sticky="w")
ttk.Radiobutton(root, text="Separate by Folders", variable=mode, value="Separate by Folders").grid(row=2, column=1, padx=10, pady=10, sticky="e")

ttk.Label(root, text="Organize By:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
ttk.Radiobutton(root, text="Content", variable=organize_by, value="Content").grid(row=3, column=1, padx=10, pady=10, sticky="w")
ttk.Radiobutton(root, text="Extension", variable=organize_by, value="Extension").grid(row=3, column=1, padx=10, pady=10, sticky="e")

ttk.Button(root, text="Organize Files", command=lambda: classify_and_organize_files(source_path.get(), destination_path.get(), mode.get(), organize_by.get())).grid(row=4, column=0, columnspan=3, padx=10, pady=20)

# Progress bar
ttk.Label(root, text="Progress:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
ttk.Progressbar(root, variable=progress_var, maximum=100).grid(row=5, column=1, padx=10, pady=10, sticky="w")


# Start the main event loop
root.mainloop()