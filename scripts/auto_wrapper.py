import os

WRAPPER_CODE = """
# --- AUTO-GENERATED KIVY WRAPPER ---
# This wraps your logic.py into a visible Android App
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import sys
import threading

# Redirect print statements to the UI
class OutputLogger:
    def __init__(self, label):
        self.label = label
    def write(self, string):
        self.label.text += string
    def flush(self):
        pass

class MyApp(App):
    def build(self):
        self.title = "My Python App"
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Starting app...\\n", halign='left', valign='top')
        self.label.bind(size=self.label.setter('text_size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.label)
        layout.add_widget(scroll)
        
        # Redirect stdout to the label
        sys.stdout = OutputLogger(self.label)
        
        # Run your logic in a thread so UI doesn't freeze
        threading.Thread(target=self.run_logic, daemon=True).start()
        return layout

    def run_logic(self):
        try:
            import logic  # This imports your original main.py (renamed)
            if hasattr(logic, 'main'):
                logic.main()
        except Exception as e:
            print(f"Error in logic: {e}")

if __name__ == '__main__':
    MyApp().run()
"""

def wrap_if_needed():
    if not os.path.exists("main.py"):
        return

    with open("main.py", "r") as f:
        content = f.read()

    # If it's already a Kivy app, do nothing
    if "kivy" in content.lower() and "app" in content.lower():
        print("✅ Kivy app detected. Skipping wrapper.")
        return

    print("🪄 No UI detected. Wrapping logic in Kivy interface...")
    
    # 1. Rename main.py to logic.py
    os.rename("main.py", "logic.py")
    
    # 2. Create new main.py with the wrapper
    with open("main.py", "w") as f:
        f.write(WRAPPER_CODE)
        
    print("✅ Wrapper applied successfully.")

if __name__ == "__main__":
    wrap_if_needed()
