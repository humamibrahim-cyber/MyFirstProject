def format_number(number: float) -> str:
    """Display whole numbers without an unnecessary .0."""
    return f"{number:g}"


def calculate(first_number: float, operation: str, second_number: float) -> float:
    """Calculate and return the result of a supported arithmetic operation."""
    if operation == "+":
        return first_number + second_number
    if operation == "-":
        return first_number - second_number
    if operation == "*":
        return first_number * second_number
    if operation == "/":
        if second_number == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return first_number / second_number

    raise ValueError("Invalid operation. Please use +, -, *, or /.")


def show_calculation(
    first_number: float, operation: str, second_number: float, result: float
) -> None:
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


def show_calculation_graph(
    first_number: float, operation: str, second_number: float, result: float
) -> None:
    """Open a window containing a bar graph of the calculation values."""
    try:
        import tkinter as tk
    except ImportError:
        print("Graph could not be opened because Tkinter is not installed.")
        return

    try:
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

        close_button = tk.Button(
            window, text="Close", command=window.destroy, width=12
        )
        close_button.pack(pady=(0, 12))

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

        # Keep the graph visible briefly, while still allowing the program to end.
        window.after(5000, window.destroy)
        window.mainloop()
    except tk.TclError as error:
        print(f"Graph could not be opened: {error}")


def main() -> None:
    """Run the interactive calculator."""
    print("Simple Calculator")

    try:
        first_number = float(input("Enter the first number: ").strip())
        operation = input("Enter an operation (+, -, *, /): ").strip()
        second_number = float(input("Enter the second number: ").strip())
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return

    try:
        result = calculate(first_number, operation, second_number)
    except (ValueError, ZeroDivisionError) as error:
        print(error)
        return

    show_calculation(first_number, operation, second_number, result)
    print(f"\nResult: {format_number(result)}")
    show_calculation_graph(first_number, operation, second_number, result)


if __name__ == "__main__":
    main()
