#2clicks

import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, ttk
import re

def load_data(file_path):
    if file_path.endswith('.xlsx'):
        return pd.read_excel(
file_path
)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format")

def find_relevant_columns(df, header_keywords):
    relevant_columns = [column for keyword in header_keywords for column in df.columns if keyword.lower() in column.lower()]
    if not relevant_columns:
        raise ValueError("Relevant columns not found based on header keywords")
    return relevant_columns

def process_data(df, header_keywords, class_keywords):
    print("Finding relevant columns...")
    relevant_columns = find_relevant_columns(df, header_keywords)
    print("Relevant columns:", relevant_columns)
    
    class_column = None
    for column in df.columns:
        if any(df[column].astype(str).str.lower().str.contains(keyword.lower()).any() for keyword in class_keywords):
            class_column = column
            break

    if not class_column:
        raise ValueError("Class column not found based on class keywords within the data")
    print("Class column identified:", class_column)

    df['Class'] = df[class_column].apply(lambda cell: ' '.join([keyword.title() for keyword in class_keywords if keyword.lower() in str(cell).lower()]))
    
    relevant_columns.remove(class_column)  
    relevant_columns_reordered = [column for keyword in header_keywords for column in relevant_columns if keyword.lower() in column.lower()]
                
    print("Relevant columns reordered:", relevant_columns_reordered)

    if not relevant_columns_reordered:
        raise ValueError("No relevant columns found after reordering.")

    combined_data = df[relevant_columns_reordered].apply(lambda row: ' '.join([str(row[column]).title() for column in relevant_columns_reordered]), axis=1)
    output_df = pd.DataFrame({'Class': df['Class'], 'Combined': combined_data})
    print("Output dataframe created")
    return output_df.to_csv(index=False, header=False, sep='|')

def create_directories_from_csv(csv_data, base_path, custom_dir_name, progress_var, root):
    if not custom_dir_name.strip():
        custom_dir_name = "output"  # Default directory name if not specified
    lines = csv_data.strip().split('\n')
    total_lines = len(lines)
    for index, line in enumerate(lines, start=1):
        class_name, combined_name = line.split('|')
        class_name_sanitized = sanitize_for_path(class_name.strip())
        combined_name_sanitized = sanitize_for_path(combined_name.strip())
        
        class_dir = os.path.join(base_path, custom_dir_name, class_name_sanitized)
        os.makedirs(class_dir, exist_ok=True)
        
        sub_dir = os.path.join(class_dir, combined_name_sanitized)
        os.makedirs(sub_dir, exist_ok=True)
        print(f"Created directory: {sub_dir}")

        progress = (index / total_lines) * 100
        progress_var.set(progress)
        root.update_idletasks()

def sanitize_for_path(name):
    return re.sub(r'[<>:"\/\\|?*]', '', name)

def main(file_path, base_path, custom_dir_name, progress_var, root):
    header_keywords = ['first', 'last', 'horse', 'pinney', 'class']
    class_keywords = ['novice', 'training', 'starter', 'modified', 'introductory', 'dressage']
    df = load_data(file_path)
    csv_data = process_data(df, header_keywords, class_keywords)
    create_directories_from_csv(csv_data, base_path, custom_dir_name, progress_var, root)

def select_file():
    file_path = filedialog.askopenfilename()
    return file_path

def select_directory():
    directory_path = filedialog.askdirectory()
    return directory_path

if __name__ == "__main__":
    root = tk.Tk()
    root.title("2 Clicks")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    file_path_var = tk.StringVar()
    base_path_var = tk.StringVar()
    progress_var = tk.DoubleVar()
    custom_dir_name_var = tk.StringVar()  # For custom directory name

    def update_file_path_label():
        file_path_label.config(text=file_path_var.get())

    def update_base_path_label():
        base_path_label.config(text=base_path_var.get())

    custom_dir_name_label = tk.Label(frame, text="Enter Event Name:")
    custom_dir_name_label.pack()
    custom_dir_name_entry = tk.Entry(frame, textvariable=custom_dir_name_var)
    custom_dir_name_entry.pack(fill='x', pady=5)

    select_file_button = tk.Button(frame, text="Select Source File", command=lambda: [file_path_var.set(select_file()), update_file_path_label()])
    select_file_button.pack(fill='x')

    file_path_label = tk.Label(frame, textvariable=file_path_var)
    file_path_label.pack(fill='x', pady=5)

    select_base_path_button = tk.Button(frame, text="Select Creation Location", command=lambda: [base_path_var.set(select_directory()), update_base_path_label()])
    select_base_path_button.pack(fill='x', pady=5)

    base_path_label = tk.Label(frame, textvariable=base_path_var)
    base_path_label.pack(fill='x', pady=5)

    start_button = tk.Button(frame, text="Start Processing", command=lambda: main(file_path_var.get(), base_path_var.get(), custom_dir_name_var.get(), progress_var, root))
    start_button.pack(fill='x')

    progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    progress_bar.pack(fill='x', pady=20)

 # Print text at the bottom right corner
    printed_text = tk.Label(root, text="Made especially for SDH Photography", anchor="se")
    printed_text.place(relx=1, rely=1, anchor="se", x=-10, y=-5)
    
    root.mainloop()
