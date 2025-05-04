import os
import sys

# Define the target directory relative to the script's location
# Assuming the script runs from h:\screentime\version 3
target_dir_relative = os.path.join('dist', 'screentime', 'PyQt5')
target_dir_absolute = os.path.abspath(target_dir_relative)

output_file = 'required_file_list.txt'

# The base directory relative to which paths should be calculated
# The example 'pyqt5\QtChart.pyd' implies the path should be relative to 'dist\screentime'
base_dir_relative = os.path.join('dist', 'screentime')
base_dir_absolute = os.path.abspath(base_dir_relative)

# Ensure the target directory exists
if not os.path.isdir(target_dir_absolute):
    print(f"Error: Target directory '{target_dir_absolute}' not found.")
    sys.exit(1) # Exit with an error code

file_list = []
print(f"Scanning directory: {target_dir_absolute}")
for root, dirs, files in os.walk(target_dir_absolute):
    for file in files:
        full_path = os.path.join(root, file)
        # Calculate path relative to base_dir_absolute
        relative_path = os.path.relpath(full_path, base_dir_absolute)
        # Ensure backslashes are used as per the example and Windows path convention
        relative_path = relative_path.replace('/', '\\')
        file_list.append(relative_path)
        # print(f"Found: {relative_path}") # Optional: print found files during scan

# Sort the list for consistency
file_list.sort()

# Write the list to the output file
try:
    with open(output_file, 'w') as f:
        for item in file_list:
            f.write(f"{item}\n")
    print(f"File list successfully written to '{output_file}' ({len(file_list)} files found).")
except IOError as e:
    print(f"Error writing to file '{output_file}': {e}")
    sys.exit(1) # Exit with an error code