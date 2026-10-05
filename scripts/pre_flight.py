import sys
import os

def check_compatibility():
    if not os.path.exists("main.py"):
        print("✅ No main.py found. Wrapper will handle it.")
        return

    with open("main.py", "r") as f:
        content = f.read().lower()

    # List of libraries that CANNOT run on Android
    blacklist = ["tkinter", "pyqt", "pyside", "wx", "customtkinter"]
    
    for lib in blacklist:
        if f"import {lib}" in content or f"from {lib}" in content:
            print(f"❌ FATAL: Detected '{lib}' in main.py.")
            print("💡 Android does not support desktop UI libraries.")
            print("💡 SOLUTION: Rewrite your UI using 'kivy' or 'flet'.")
            sys.exit(1) # This fails the GitHub Action immediately

    print("✅ Pre-flight check passed. Code is compatible.")

if __name__ == "__main__":
    check_compatibility()
