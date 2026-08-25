print("Simple Calculator")

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
        print(f"Result: {result}")
except ValueError:
    print("Invalid input. Please enter valid numbers.")
except ZeroDivisionError:
    print("Cannot divide by zero.")
