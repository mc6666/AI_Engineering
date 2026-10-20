def calculate(expression):
    try:
        allowed = set("0123456789+-*/(). %")
        if not all(c in allowed for c in expression):
            return "Error: invalid characters in expression"
        result = eval(expression)
        if isinstance(result, float):
            result = round(result, 10)
        return result
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception:
        return "Error: invalid expression"


def main():
    print("=" * 36)
    print("   Python Calculator")
    print("   Type 'quit' or 'exit' to close")
    print("=" * 36)
    print("Operators: + - * / // % ** ()")
    print()

    while True:
        try:
            expr = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not expr:
            continue
        if expr.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        print(calculate(expr))


if __name__ == "__main__":
    main()
