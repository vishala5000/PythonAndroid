from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

class CalculatorApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        self.main_layout = GridLayout(cols=4, padding=15, spacing=10)
        
        self.display = Label(
            text="0", 
            font_size="48sp", 
            halign="right", 
            valign="middle", 
            size_hint_y=0.2,
            color=(1, 1, 1, 1)
        )
        self.display.bind(size=self._update_label_size)
        self.main_layout.add_widget(self.display)
        
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['.', '0', '=', '+'],
            ['C']
        ]
        
        for row in buttons:
            if len(row) == 1:
                btn = Button(
                    text=row[0], 
                    size_hint_y=0.2, 
                    font_size="36sp", 
                    background_color=(0.8, 0.2, 0.2, 1),
                    color=(1, 1, 1, 1)
                )
                btn.bind(on_press=self.clear_display)
                self.main_layout.add_widget(btn)
            else:
                for btn_text in row:
                    btn = Button(text=btn_text, font_size="36sp", color=(1, 1, 1, 1))
                    if btn_text == '=':
                        btn.bind(on_press=self.calculate)
                        btn.background_color = (0.2, 0.7, 0.3, 1)
                    elif btn_text in ['+', '-', '*', '/']:
                        btn.background_color = (0.2, 0.4, 0.8, 1)
                    else:
                        btn.bind(on_press=self.on_button_press)
                    self.main_layout.add_widget(btn)
                    
        return self.main_layout

    def _update_label_size(self, instance, value):
        instance.text_size = instance.size

    def on_button_press(self, instance):
        current = self.display.text
        if current == '0' or current == 'Error':
            self.display.text = instance.text
        else:
            self.display.text = current + instance.text

    def calculate(self, instance):
        try:
            expression = self.display.text
            if all(c in '0123456789+-*/. ' for c in expression):
                result = str(eval(expression))
                if result.endswith('.0'):
                    result = result[:-2]
                self.display.text = result
            else:
                self.display.text = 'Error'
        except Exception:
            self.display.text = 'Error'

    def clear_display(self, instance):
        self.display.text = '0'

def main():
    CalculatorApp().run()

if __name__ == '__main__':
    main()
