import operator
from typing import Callable, NamedTuple

# Each operation maps to the function that performs it and the sentence used to
# explain it. Adding a new operation only requires a new entry here.
OPERATIONS: dict[str, tuple[Callable[[float, float], float], str]] = {
    "+": (operator.add, "Add the two numbers"),
    "-": (operator.sub, "Subtract the second number from the first"),
    "*": (operator.mul, "Multiply the two numbers"),
    "/": (operator.truediv, "Divide the first number by the second"),
    "**": (operator.pow, "Raise the first number to the power of the second"),
    "//": (operator.floordiv, "Divide, then keep only the whole number part"),
    "%": (operator.mod, "Divide, then keep only the remainder"),
}

# Built from OPERATIONS so prompts and error messages stay in step with it.
SUPPORTED_OPERATIONS = ", ".join(OPERATIONS)


class Calculation(NamedTuple):
    """One completed calculation, kept together so it cannot be mis-ordered."""

    first_number: float
    operation: str
    second_number: float
    result: float


def format_number(number: float) -> str:
    """Display whole numbers without an unnecessary .0.

    15 significant digits is the most a float can be trusted to carry, so this
    shows large values in full while still hiding binary rounding noise such as
    the trailing digits of 0.1 + 0.2.
    """
    return f"{number:.15g}"


def calculate(first_number: float, operation: str, second_number: float) -> float:
    """Calculate and return the result of a supported arithmetic operation."""
    if operation not in OPERATIONS:
        raise ValueError(f"Invalid operation. Please use {SUPPORTED_OPERATIONS}.")
    if operation in {"/", "//", "%"} and second_number == 0:
        raise ZeroDivisionError("Cannot divide by zero.")

    apply_operation, _ = OPERATIONS[operation]
    return apply_operation(first_number, second_number)


def read_float(prompt: str) -> float:
    """Ask for a number until a valid one is entered."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def read_operation(prompt: str) -> str:
    """Ask for an operation until a supported one is entered."""
    while True:
        operation = input(prompt).strip()
        if operation in OPERATIONS:
            return operation
        print(f"Invalid operation. Please use {SUPPORTED_OPERATIONS}.")


def show_calculation(calculation: Calculation) -> None:
    """Show a simple visual explanation of how the answer was calculated."""
    first = format_number(calculation.first_number)
    second = format_number(calculation.second_number)
    answer = format_number(calculation.result)

    # The operator sits in its own two-character column to the left of the
    # numbers, so the number column width depends only on the numbers.
    operator_column = 2
    width = max(len(first), len(second), len(answer))
    _, description = OPERATIONS[calculation.operation]

    print("\nHow the result was calculated:")
    print(f"1. {description}")
    print(f"2. {first} {calculation.operation} {second} = {answer}\n")
    print(f"{'':>{operator_column}}{first:>{width}}")
    print(f"{calculation.operation:<{operator_column}}{second:>{width}}")
    print(f"{'':>{operator_column}}{'-' * width}")
    print(f"{'':>{operator_column}}{answer:>{width}}")


def show_calculation_graph(calculation: Calculation) -> None:
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

        canvas_width = 760
        canvas_height = 390
        # Labels get a reserved gutter on the left so a long negative bar can
        # never grow underneath them.
        label_gutter = 140
        zero_x = (label_gutter + canvas_width - 40) // 2
        canvas = tk.Canvas(
            window, width=canvas_width, height=canvas_height, bg="white"
        )
        canvas.pack(padx=12, pady=12)

        close_button = tk.Button(
            window, text="Close", command=window.destroy, width=12
        )
        close_button.pack(pady=(0, 12))

        equation = (
            f"{format_number(calculation.first_number)} {calculation.operation} "
            f"{format_number(calculation.second_number)} = "
            f"{format_number(calculation.result)}"
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

        rows = [
            ("First number", calculation.first_number, "#3b82f6"),
            ("Second number", calculation.second_number, "#f59e0b"),
            ("Result", calculation.result, "#22c55e"),
        ]
        largest_value = max(abs(value) for _, value, _ in rows) or 1
        scale = 215 / largest_value

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
    except tk.TclError as error:
        print(f"Graph could not be opened: {error}")


def main() -> None:
    """Run the interactive calculator."""
    print("Simple Calculator")

    try:
        first_number = read_float("Enter the first number: ")
        operation = read_operation(f"Enter an operation ({SUPPORTED_OPERATIONS}): ")
        second_number = read_float("Enter the second number: ")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return

    try:
        result = calculate(first_number, operation, second_number)
    except (ValueError, ZeroDivisionError) as error:
        print(error)
        return

    calculation = Calculation(first_number, operation, second_number, result)
    show_calculation(calculation)
    print(f"\nResult: {format_number(result)}")
    show_calculation_graph(calculation)


if __name__ == "__main__":
    main()
