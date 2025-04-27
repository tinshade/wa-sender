import pyperclip
import os
def copy_file_to_clipboard(file_path):
    """Copies the content of a file to the clipboard.

    Args:
        file_path: The path to the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            pyperclip.copy(content)
            print(f"Content of '{file_path}' copied to clipboard.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except pyperclip.PyperclipException as e:
        print(f"Error: {e}. Ensure you have a copy/paste mechanism installed (like xclip or xsel on Linux).")

# Example usage:
file_path = os.path.join(os.getcwd(), 'data', 'message.txt')  # Replace with the actual path to your file
copy_file_to_clipboard(file_path)