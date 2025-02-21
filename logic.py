import math
import ast

def Calculate(expression):
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return result
    except Exception:
        return "Syntax error"