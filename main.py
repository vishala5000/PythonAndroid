from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class CalculatorApp(App):
    def build(self):
        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Display Screen
        self.display = Label(
            text="0",
            font_size=60,
            size_hint=(1, 0.2),
            halign='right',
            valign='middle',
            color=(1, 1, 1, 1),
            background_color=(0.1, 0.1, 0.1, 1)
        )
        # Bind text size to widget size for proper alignment
        self.display.bind(size=self.display.setter('text_size'))
        main_layout.add_widget(self.display)

        # Grid for Buttons (4 columns)
        grid = GridLayout(cols=4, spacing=10, size_hint=(1, 0.8))

        # Define button layout
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '.', '+',
            '='
        ]

        for btn_text in buttons:
            if btn_text == '=':
                # Make the '=' button span the whole row visually
                btn = Button(text=btn_text, font_size=40, background_color=(0, 0.6, 0, 1))
                btn.bind(on_press=self.on_calculate)
                grid.add_widget(btn)
                # Add 3 invisible labels to fill the rest of the row
                for _ in range(3):
                    grid.add_widget(Label(text=''))
            else:
                btn = Button(text=btn_text, font_size=40)
                
                # Color coding for better UX
                if btn_text == 'C':
                    btn.bind(on_press=self.on_clear)
                    btn.background_color = (0.8, 0.2, 0.2, 1) # Red for Clear
                elif btn_text in ['+', '-', '*', '/']:
                    btn.bind(on_press=self.on_operator)
                    btn.background_color = (0.3, 0.3, 0.3, 1) # Dark grey for operators
                else:
                    btn.bind(on_press=self.on_number)
                    btn.background_color = (0.2, 0.2, 0.2, 1) # Lighter grey for numbers
                    
                grid.add_widget(btn)

        main_layout.add_widget(grid)
        return main_layout

    def on_number(self, instance):
        """Handles number and decimal button presses"""
        if self.display.text == "0" and instance.text != '.':
            self.display.text = instance.text
        else:
            self.display.text += instance.text

    def on_operator(self, instance):
        """Handles operator button presses"""
        self.display.text += instance.text

    def on_clear(self, instance):
        """Clears the display"""
        self.display.text = "0"

    def on_calculate(self, instance):
        """Calculates the result safely"""
        try:
            # Evaluate the math expression
            result = str(eval(self.display.text))
            self.display.text = result
        except Exception:
            # Catch any math errors (like dividing by zero or invalid syntax)
            self.display.text = "Error"

if __name__ == '__main__':
    CalculatorApp().run()
