from android.widget import LinearLayout, TextView, Button
from android.view import ViewGroup, View, Gravity
from android.graphics import Color

def main(text_view):
    parent = text_view.getParent()
    if not isinstance(parent, ViewGroup):
        return
        
    parent.removeAllViews()
    context = text_view.getContext()
    
    # 1. Main Layout (Dark Theme)
    main_layout = LinearLayout(context)
    main_layout.setOrientation(LinearLayout.VERTICAL)
    main_layout.setBackgroundColor(Color.parseColor("#121212"))
    main_layout.setPadding(30, 60, 30, 30)
    
    # 2. Display Screen
    display = TextView(context)
    display.setBackgroundColor(Color.parseColor("#1E1E1E"))
    display.setTextColor(Color.parseColor("#BB86FC")) # Purple accent
    display.setTextSize(48.0)
    display.setPadding(20, 40, 20, 40)
    display.setText("0")
    display.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL)
    
    main_layout.addView(display, LinearLayout.LayoutParams(
        LinearLayout.LayoutParams.MATCH_PARENT,
        0, 1.0  # Weight 1.0 pushes buttons to the bottom
    ))
    
    # 3. Button Definitions: (text, bg_color, text_color, weight)
    buttons_rows = [
        [("C", "#CF6679", "#000000", 1), ("±", "#333333", "#FFFFFF", 1), ("%", "#333333", "#FFFFFF", 1), ("÷", "#BB86FC", "#000000", 1)],
        [("7", "#333333", "#FFFFFF", 1), ("8", "#333333", "#FFFFFF", 1), ("9", "#333333", "#FFFFFF", 1), ("×", "#BB86FC", "#000000", 1)],
        [("4", "#333333", "#FFFFFF", 1), ("5", "#333333", "#FFFFFF", 1), ("6", "#333333", "#FFFFFF", 1), ("-", "#BB86FC", "#000000", 1)],
        [("1", "#333333", "#FFFFFF", 1), ("2", "#333333", "#FFFFFF", 1), ("3", "#333333", "#FFFFFF", 1), ("+", "#BB86FC", "#000000", 1)],
        [("0", "#333333", "#FFFFFF", 2), (".", "#333333", "#FFFFFF", 1), ("=", "#03DAC6", "#000000", 1)] # 0 spans 2 columns
    ]
    
    current_expression = [""]
    
    # 4. Click Handler
    class ClickListener(View.OnClickListener):
        def onClick(self, view):
            text = str(view.getText())
            if text == "C":
                current_expression[0] = ""
                display.setText("0")
            elif text == "±":
                if current_expression[0].startswith("-"):
                    current_expression[0] = current_expression[0][1:]
                else:
                    current_expression[0] = "-" + current_expression[0]
                display.setText(current_expression[0] or "0")
            elif text == "%":
                try:
                    val = eval(current_expression[0]) / 100
                    current_expression[0] = str(val)
                    display.setText(current_expression[0])
                except Exception:
                    display.setText("Error")
                    current_expression[0] = ""
            elif text == "=":
                try:
                    if not current_expression[0]:
                        return
                    # Safely evaluate math expression
                    expr = current_expression[0].replace("×", "*").replace("÷", "/")
                    result = eval(expr)
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    current_expression[0] = str(result)
                    display.setText(current_expression[0])
                except Exception:
                    display.setText("Error")
                    current_expression[0] = ""
            else:
                current_expression[0] += text
                display.setText(current_expression[0])

    click_listener = ClickListener()
    
    # 5. Generate Button Rows
    for row in buttons_rows:
        row_layout = LinearLayout(context)
        row_layout.setOrientation(LinearLayout.HORIZONTAL)
        
        for btn_text, bg_color, txt_color, weight in row:
            btn = Button(context)
            btn.setText(btn_text)
            btn.setTextColor(Color.parseColor(txt_color))
            btn.setBackgroundColor(Color.parseColor(bg_color))
            btn.setTextSize(28.0)
            btn.setGravity(Gravity.CENTER)
            btn.setOnClickListener(click_listener)
            
            # Add margins
            params = LinearLayout.LayoutParams(0, 180, weight) # height=180px
            params.setMargins(10, 10, 10, 10)
            btn.setLayoutParams(params)
            
            row_layout.addView(btn)
            
        main_layout.addView(row_layout, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ))
        
    # 6. Add the new calculator UI to the screen
    parent.addView(main_layout, ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.MATCH_PARENT
    ))
