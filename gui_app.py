import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from inference import predict_image, classify_text, extract_text_from_file
import re
import threading

# Add EasyOCR functionality
try:
    import easyocr
    _reader = None
    
    def get_ocr_reader():
        global _reader
        if _reader is None:
            print("Loading EasyOCR model (first time only)...")
            _reader = easyocr.Reader(['en'])  # Initialize once for English
        return _reader
    
    def perform_ocr(image_path):
        try:
            reader = get_ocr_reader()
            results = reader.readtext(image_path)
            # Extract all text components and join them
            extracted_text = " ".join([text for _, text, _ in results])
            return extracted_text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    HAS_OCR = True
except ImportError:
    print("EasyOCR not found. To enable OCR features, install it with: pip install easyocr")
    HAS_OCR = False
    
    def perform_ocr(image_path):
        return ""

# Add a new variable to track file operation mode


# Function to classify and organize files
def classify_and_organize_files(source_path, destination_path, mode, organize_by, should_copy=True):
    if not os.path.exists(source_path):
        messagebox.showerror("Error", "Source path does not exist.")
        return

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
        
    # Get all organized category folders
    organized_folders = ["images", "documents", "videos", "audios", "software", "archives", "others", "datasheets"]
    skipped_files = 0
    existing_files = 0

    files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
    total_files = len(files)
    processed_files = 0

    # Categories for text-based files
    text_categories = {
        "books": "Educational materials, textbooks, novels, fiction, non-fiction literature",
        "documents": "Official papers, reports, certificates, formal documentation",
        "stories": "Narratives, creative writing, short stories, personal accounts",
        "assignments": "School or university homework, projects, academic tasks",
        "magazines": "Periodicals, articles, news publications, journals",
        "financials": "Financial statements, invoices, receipts, banking documents",
        "technical": "Technical documentation, manuals, specifications, guides",
        "personal": "Personal letters, notes, diaries, messages",
        "academic": "Research papers, scholarly articles, academic publications"
    }

    for file_name in files:
        file_path = os.path.join(source_path, file_name)
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()
        

        if organize_by == "Content":
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                try:
                    # First use image classification
                    image_category = predict_image(file_path)
                    
                    # If it looks like text content and OCR is available, try OCR
                    if HAS_OCR and image_category.lower() in ['text']:
                        print(f"Image may contain text, applying OCR to: {file_name}")
                        extracted_text = perform_ocr(file_path)
                        
                        if extracted_text and len(extracted_text.strip()) > 20:
                            print(f"Extracted {len(extracted_text)} characters from image")
                            text_category = classify_text(extracted_text, text_categories)
                            category = f"images/{text_category}"
                        else:
                            category = f"images/{image_category}"
                    else:
                        category = f"images/{image_category}"
                except Exception as e:
                    print(f"Error classifying image {file_path}: {e}")
                    category = "images/unknown"
            elif ext in ['.pdf', '.docx', '.txt', '.md']:
                # Use text classification for document files
                try:
                    text_content = extract_text_from_file(file_path)
                    if text_content:
                        text_category = classify_text(text_content, text_categories)
                        category = f"documents/{text_category}"
                    else:
                        category = "documents/unknown"
                except Exception as e:
                    print(f"Error classifying document {file_path}: {e}")
                    category = "documents/unknown"
            elif ext in ['.csv', '.xlsx']:
                category = "datasheets"
            elif ext in ['.mp4', '.mkv', '.webm']:
                category = "videos"
            elif ext in ['.mp3', '.wav']:
                category = "audios"
            elif ext in ['.zip', '.rar', '.7z']:
                category = "archives"
            else:
                category = "others"
        else:
            # Organize by extension
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                category = "images"
            elif ext in ['.pdf', '.docx', '.ppt', '.txt']:
                category = "documents"
            elif ext in ['.csv', '.xlsx']:
                category = "datasheets"
            elif ext in ['.mp4', '.mkv', '.webm']:
                category = "videos"
            elif ext in ['.mp3', '.wav']:
                category = "audios"
            elif ext in ['.exe', '.apk', '.msi']:
                category = "software"
            elif ext in ['.zip', '.rar', '.7z']:
                category = "archives"
            else:
                category = "others"
                
        # Create target path based on mode
        if mode == "Separate by Folders":
            # Create the target directory and copy/move the file
            target_dir = os.path.join(destination_path, category)
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, file_name)
        else:
            # Keep in the same location but rename with category prefix
            category_name = category.split('/')[-1] if '/' in category else category
            name, extension = os.path.splitext(file_name)
            target_path = os.path.join(destination_path, f"{name}_({category_name}){extension}")

        # Check if the file already exists at destination
        if os.path.exists(target_path):
            print(f"File already exists at destination: {target_path}")
            existing_files += 1
        else:
            try:
                # Copy or move the file based on user selection
                if should_copy:
                    shutil.copy2(file_path, target_path)
                    print(f"Copied: {file_name} to {target_path}")
                else:
                    shutil.move(file_path, target_path)
                    print(f"Moved: {file_name} to {target_path}")
            except Exception as e:
                print(f"Error handling {file_path}: {e}")

        # Update progress bar
        processed_files += 1
        progress_var.set((processed_files / total_files) * 100)
        progress_label.config(text=f"{processed_files}/{total_files} files processed")
        root.update_idletasks()
                
    # Show results including skipped and existing files
    result_message = f"Successfully processed {processed_files - existing_files} files.\n"
    if existing_files > 0:
        result_message += f"Skipped {existing_files} files that already exist at destination."
    
    messagebox.showinfo("Operation Complete", result_message)

# Updated function to start the organization process
def start_organization():
    src = source_path.get()
    dest = destination_path.get()
    if not src or not dest:
        messagebox.showerror("Error", "Please select both source and destination directories.")
        return
    
    # Disable the organize button to prevent multiple clicks
    organize_button.config(state=tk.DISABLED)
    
    # Start the classification in a separate thread
    thread = threading.Thread(
        target=classify_and_organize_files,
        args=(src, dest, mode.get(), organize_by.get(), copy_files.get())
    )
    thread.daemon = True
    thread.start()
    
    # Check if the thread is still running
    def check_thread():
        if thread.is_alive():
            root.after(100, check_thread)
        else:
            organize_button.config(state=tk.NORMAL)
    
    root.after(100, check_thread)

# Function to browse for source path
def browse_source():
    source_path.set(filedialog.askdirectory())

# Function to browse for destination path
def browse_destination():
    destination_path.set(filedialog.askdirectory())

# Create the main application window
root = tk.Tk()
root.title("Smart File Organizer")
root.geometry("600x450")
root.resizable(True, True)

# Create and place widgets
source_path = tk.StringVar()
destination_path = tk.StringVar()
mode = tk.StringVar(value="Separate by Folders")
organize_by = tk.StringVar(value="Content")
progress_var = tk.DoubleVar()
copy_files = tk.BooleanVar(value=True)

# Main frame
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)


# Source path
ttk.Label(main_frame, text="Source Path:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
ttk.Entry(main_frame, textvariable=source_path, width=50).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
ttk.Button(main_frame, text="Browse", command=browse_source).grid(row=0, column=2, padx=10, pady=10)

# Destination path
ttk.Label(main_frame, text="Destination Path:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
ttk.Entry(main_frame, textvariable=destination_path, width=50).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
ttk.Button(main_frame, text="Browse", command=browse_destination).grid(row=1, column=2, padx=10, pady=10)

# Mode options
mode_frame = ttk.LabelFrame(main_frame, text="Organization Mode")
mode_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
ttk.Radiobutton(mode_frame, text="Include Category in File Name", variable=mode, value="Include Class in File Name").pack(side=tk.LEFT, padx=20, pady=5)
ttk.Radiobutton(mode_frame, text="Separate by Folders", variable=mode, value="Separate by Folders").pack(side=tk.RIGHT, padx=20, pady=5)

# Organization by options
organize_frame = ttk.LabelFrame(main_frame, text="Organize Files By")
organize_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
ttk.Radiobutton(organize_frame, text="Content Analysis (AI)", variable=organize_by, value="Content").pack(side=tk.LEFT, padx=20, pady=5)
ttk.Radiobutton(organize_frame, text="File Extension", variable=organize_by, value="Extension").pack(side=tk.RIGHT, padx=20, pady=5)

# Add after the organization by options
file_op_frame = ttk.LabelFrame(main_frame, text="File Operation")
file_op_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
ttk.Radiobutton(file_op_frame, text="Copy Files", variable=copy_files, value=True).pack(side=tk.LEFT, padx=20, pady=5)
ttk.Radiobutton(file_op_frame, text="Move Files", variable=copy_files, value=False).pack(side=tk.RIGHT, padx=20, pady=5)

# Update the organize button to row 5
organize_button = ttk.Button(main_frame, text="Organize Files", command=start_organization)
organize_button.grid(row=5, column=0, columnspan=3, padx=10, pady=20)

# Update progress bar to row 6
progress_frame = ttk.Frame(main_frame)
progress_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=400).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
progress_label = ttk.Label(progress_frame, text="0/0 files processed")
progress_label.pack(side=tk.LEFT, padx=5)

# Configure grid weights
main_frame.columnconfigure(1, weight=1)

# Start the main event loop
root.mainloop()