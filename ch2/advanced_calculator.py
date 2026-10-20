import tkinter as tk
from tkinter import ttk, messagebox
import math
import datetime
import speech_recognition as sr
import threading

# =========================
# Advanced Calculator Class
# =========================

class AdvancedCalculator:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced AI Calculator")
        self.root.geometry("700x650")

        self.expression = ""
        self.memory = 0

        self.equation = tk.StringVar()

        self.create_ui()
        self.bind_keyboard()

    # =========================
    # UI
    # =========================

    def create_ui(self):

        # Display
        self.entry = tk.Entry(
            self.root,
            textvariable=self.equation,
            font=("Arial", 24),
            bd=10,
            relief=tk.RIDGE,
            justify="right"
        )

        self.entry.pack(fill="x", padx=10, pady=10)

        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="left", fill="both", expand=True)

        # History Frame
        history_frame = tk.Frame(self.root)
        history_frame.pack(side="right", fill="y")

        tk.Label(
            history_frame,
            text="History",
            font=("Arial", 16)
        ).pack()

        self.history_list = tk.Listbox(
            history_frame,
            width=30,
            font=("Arial", 12)
        )

        self.history_list.pack(fill="y", expand=True)

        # Buttons
        buttons = [
            ['7', '8', '9', '/', 'sqrt'],
            ['4', '5', '6', '*', '^'],
            ['1', '2', '3', '-', 'sin'],
            ['0', '.', '=', '+', 'cos'],
            ['(', ')', 'C', 'DEL', 'tan'],
            ['log', 'ln', 'π', 'e', 'AI'],
            ['MC', 'MR', 'M+', 'M-', 'VOICE']
        ]

        for r, row in enumerate(buttons):
            for c, btn in enumerate(row):

                action = lambda x=btn: self.click(x)

                tk.Button(
                    button_frame,
                    text=btn,
                    width=8,
                    height=3,
                    font=("Arial", 14),
                    command=action
                ).grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        for i in range(7):
            button_frame.grid_rowconfigure(i, weight=1)

        for i in range(5):
            button_frame.grid_columnconfigure(i, weight=1)

    # =========================
    # Keyboard Support
    # =========================

    def bind_keyboard(self):

        self.root.bind("<Key>", self.key_input)

    def key_input(self, event):

        key = event.char

        if key in "0123456789+-*/().":
            self.expression += key
            self.update_display()

        elif event.keysym == "Return":
            self.calculate()

        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.update_display()

    # =========================
    # Display
    # =========================

    def update_display(self):
        self.equation.set(self.expression)

    # =========================
    # Button Click
    # =========================

    def click(self, value):

        if value == "=":
            self.calculate()

        elif value == "C":
            self.expression = ""
            self.update_display()

        elif value == "DEL":
            self.expression = self.expression[:-1]
            self.update_display()

        elif value == "π":
            self.expression += str(math.pi)
            self.update_display()

        elif value == "e":
            self.expression += str(math.e)
            self.update_display()

        elif value == "^":
            self.expression += "**"
            self.update_display()

        elif value == "sqrt":
            self.expression += "math.sqrt("
            self.update_display()

        elif value == "sin":
            self.expression += "math.sin("
            self.update_display()

        elif value == "cos":
            self.expression += "math.cos("
            self.update_display()

        elif value == "tan":
            self.expression += "math.tan("
            self.update_display()

        elif value == "log":
            self.expression += "math.log10("
            self.update_display()

        elif value == "ln":
            self.expression += "math.log("
            self.update_display()

        elif value == "MC":
            self.memory = 0

        elif value == "MR":
            self.expression += str(self.memory)
            self.update_display()

        elif value == "M+":
            try:
                self.memory += float(eval(self.expression))
            except:
                pass

        elif value == "M-":
            try:
                self.memory -= float(eval(self.expression))
            except:
                pass

        elif value == "VOICE":
            threading.Thread(target=self.voice_input).start()

        elif value == "AI":
            self.ai_assistant()

        else:
            self.expression += value
            self.update_display()

    # =========================
    # Calculation
    # =========================

    def calculate(self):

        try:
            result = str(eval(self.expression))

            history_item = (
                f"{datetime.datetime.now().strftime('%H:%M:%S')} : "
                f"{self.expression} = {result}"
            )

            self.history_list.insert(tk.END, history_item)

            self.expression = result
            self.update_display()

        except Exception as e:
            self.equation.set("Error")
            self.expression = ""

    # =========================
    # Voice Input
    # =========================

    def voice_input(self):

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:

            self.equation.set("Listening...")

            try:
                audio = recognizer.listen(source)

                text = recognizer.recognize_google(audio)

                text = text.lower()

                replacements = {
                    "plus": "+",
                    "minus": "-",
                    "times": "*",
                    "multiply": "*",
                    "divided by": "/",
                    "divide": "/"
                }

                for word, symbol in replacements.items():
                    text = text.replace(word, symbol)

                self.expression += text
                self.update_display()

            except:
                self.equation.set("Voice Error")

    # =========================
    # AI Assistant
    # =========================

    def ai_assistant(self):

        try:

            expr = self.expression

            result = eval(expr)

            explanation = f"""
Expression:
{expr}

Result:
{result}

Explanation:
The calculator evaluated the mathematical
expression step by step using Python eval().
"""

            messagebox.showinfo("AI Math Assistant", explanation)

        except Exception as e:
            messagebox.showerror(
                "AI Assistant",
                f"Unable to analyze expression.\n{e}"
            )


# =========================
# Main
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = AdvancedCalculator(root)

    root.mainloop()