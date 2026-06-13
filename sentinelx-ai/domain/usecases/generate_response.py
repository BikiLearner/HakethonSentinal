def generate_response(mode: str, user_input: str) -> str:
    mode = mode.lower()

    if mode == "industrial":
        return (
            "Worker detected in restricted zone with rising thermal stress. "
            "Immediate safety action recommended."
        )

    elif mode == "health":
        return (
            "You appear slightly fatigued based on activity patterns. "
            "Consider taking a short break."
        )

    elif mode == "planner":
        return (
            "This task can be broken into smaller steps. "
            "Start by defining inputs, then process logic, and finally generate output."
        )

    return "System ready."