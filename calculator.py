print("Simple Calculator")


def format_number(number):
    """Display whole numbers without an unnecessary .0."""
    return f"{number:g}"


def show_calculation(first_number, operation, second_number, result):
    """Show a simple visual explanation of how the answer was calculated."""
    operation_names = {
        "+": "Add the two numbers",
        "-": "Subtract the second number from the first",
        "*": "Multiply the two numbers",
        "/": "Divide the first number by the second",
    }

    first = format_number(first_number)
    second = format_number(second_number)
    answer = format_number(result)
    width = max(len(first), len(second) + 2, len(answer))

    print("\nHow the result was calculated:")
    print(f"1. {operation_names[operation]}")
    print(f"2. {first} {operation} {second} = {answer}\n")
    print(f"   {first:>{width}}")
    print(f" {operation} {second:>{width - 2}}")
    print(f"   {'-' * width}")
    print(f"   {answer:>{width}}")


def show_calculation_graph(first_number, operation, second_number, result):
    """Open a window containing a bar graph of the calculation values."""
    try:
        import tkinter as tk

        window = tk.Tk()
        window.title("Calculation Visualization")
        window.resizable(False, False)

        canvas_width = 680
        canvas_height = 390
        zero_x = canvas_width // 2
        canvas = tk.Canvas(
            window, width=canvas_width, height=canvas_height, bg="white"
        )
        canvas.pack(padx=12, pady=12)

        equation = (
            f"{format_number(first_number)} {operation} "
            f"{format_number(second_number)} = {format_number(result)}"
        )
        canvas.create_text(
            canvas_width // 2,
            35,
            text=equation,
            font=("Arial", 22, "bold"),
            fill="#172554",
        )
        canvas.create_text(
            canvas_width // 2,
            70,
            text="Bar graph of the two inputs and the result",
            font=("Arial", 11),
            fill="#475569",
        )

        values = [first_number, second_number, result]
        largest_value = max(abs(value) for value in values) or 1
        scale = 245 / largest_value
        rows = [
            ("First number", first_number, "#3b82f6"),
            ("Second number", second_number, "#f59e0b"),
            ("Result", result, "#22c55e"),
        ]

        # The center line represents zero. Negative bars go left; positive bars go right.
        canvas.create_line(zero_x, 100, zero_x, 340, fill="#64748b", width=2)
        canvas.create_text(zero_x, 360, text="0", font=("Arial", 10, "bold"))

        for index, (label, value, color) in enumerate(rows):
            y = 135 + index * 80
            bar_end = zero_x + value * scale
            left = min(zero_x, bar_end)
            right = max(zero_x, bar_end)

            # Keep a zero-value bar visible as a thin marker.
            if left == right:
                right += 2

            canvas.create_text(
                15, y, text=label, anchor="w", font=("Arial", 11, "bold")
            )
            canvas.create_rectangle(left, y - 18, right, y + 18, fill=color, outline="")

            value_x = bar_end + (8 if value >= 0 else -8)
            value_anchor = "w" if value >= 0 else "e"
            canvas.create_text(
                value_x,
                y,
                text=format_number(value),
                anchor=value_anchor,
                font=("Arial", 11, "bold"),
            )

        window.mainloop()
    except Exception:
        print("Graph could not be opened on this computer.")

try:
    first_number = float(input("Enter the first number: "))
    operation = input("Enter an operation (+, -, *, /): ")
    second_number = float(input("Enter the second number: "))

    if operation == "+":
        result = first_number + second_number
    elif operation == "-":
        result = first_number - second_number
    elif operation == "*":
        result = first_number * second_number
    elif operation == "/":
        if second_number == 0:
            raise ZeroDivisionError
        result = first_number / second_number
    else:
        result = None
        print("Invalid operation. Please use +, -, *, or /.")

    if result is not None:
        show_calculation(first_number, operation, second_number, result)
        print(f"\nResult: {format_number(result)}")
        show_calculation_graph(first_number, operation, second_number, result)
except ValueError:
    print("Invalid input. Please enter valid numbers.")
except ZeroDivisionError:
    print("Cannot divide by zero.")
