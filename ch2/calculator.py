import tkinter as tk

# Function to update the expression
def press(num):
    global expression
    expression += str(num)
    equation.set(expression)

# Function to evaluate the final expression
def equalpress():
    global expression
    try:
        total = str(eval(expression))
        equation.set(total)
        expression = total
    except:
        equation.set("Error")
        expression = ""

# Function to clear the screen
def clear():
    global expression
    expression = ""
    equation.set("")

# Main window
gui = tk.Tk()
gui.title("Python Calculator")
gui.geometry("320x420")
gui.configure(bg="lightgray")

expression = ""
equation = tk.StringVar()

# Entry field
entry_field = tk.Entry(
    gui,
    textvariable=equation,
    font=('Arial', 20),
    bd=10,
    insertwidth=2,
    width=14,
    borderwidth=4,
    justify='right'
)

entry_field.grid(row=0, column=0, columnspan=4, pady=20)

# Button layout
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
]

# Create buttons
for (text, row, col) in buttons:
    if text == '=':
        action = equalpress
    else:
        action = lambda x=text: press(x)

    tk.Button(
        gui,
        text=text,
        padx=20,
        pady=20,
        font=('Arial', 16),
        command=action
    ).grid(row=row, column=col, sticky="nsew")

# Clear button
tk.Button(
    gui,
    text='C',
    padx=20,
    pady=20,
    font=('Arial', 16),
    command=clear,
    bg='orange'
).grid(row=5, column=0, columnspan=4, sticky="nsew")

# Make grid responsive
for i in range(6):
    gui.grid_rowconfigure(i, weight=1)

for i in range(4):
    gui.grid_columnconfigure(i, weight=1)

# Run application
gui.mainloop()