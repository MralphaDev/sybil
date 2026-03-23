import os

# Folder path relative to root
folder_path = os.path.join(os.getcwd(), "conv_tk_transf")

# Check if folder exists
if not os.path.exists(folder_path):
    print(f"Folder '{folder_path}' does not exist.")
    exit()

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    # Full path of the file
    file_path = os.path.join(folder_path, filename)
    
    # Only process CSV files containing 'token-transfer-'
    if os.path.isfile(file_path) and filename.endswith(".csv") and "token-transfer-" in filename:
        # New filename with 'token-transfer-' removed
        new_filename = filename.replace("token-transfer-", "")
        new_file_path = os.path.join(folder_path, new_filename)
        
        # Rename the file
        try:
            os.rename(file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Error renaming {filename}: {e}")

print("Renaming completed.")