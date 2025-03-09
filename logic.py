import math
import ast

def calculate(expression):
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if result % 1 == 0:
            result = int(result)
        if isinstance(result, float):
            result = "{:.2f}".format(result)
        return result
    except Exception:
        return "Syntax error"