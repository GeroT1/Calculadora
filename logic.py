import math
import ast

def calculate(expression):
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if isinstance(result, float):
            result = "{:.2f}".format(result)
        return result
    except Exception:
        return "Syntax error"