import math


def calculate(number1, number2, operation):
    if isinstance(number1, bool) or not isinstance(number1, (int, float)):
        raise ValueError("number1 must be a number")
    if isinstance(number2, bool) or not isinstance(number2, (int, float)):
        raise ValueError("number2 must be a number")
    if not math.isfinite(number1) or not math.isfinite(number2):
        raise ValueError("Numbers must be finite")

    if operation == "add":
        result = number1 + number2
    elif operation == "subtract":
        result = number1 - number2
    elif operation == "multiply":
        result = number1 * number2
    elif operation == "divide":
        if number2 == 0:
            raise ValueError("Cannot divide by zero")
        result = number1 / number2
    else:
        raise ValueError("Unsupported calculator operation")

    return result
