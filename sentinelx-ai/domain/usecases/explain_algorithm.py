def explain_algorithm(content: str) -> str:
    content_lower = content.lower()

    # 🔹 Detect common patterns
    if "for" in content_lower or "while" in content_lower:
        return (
            "This algorithm uses iteration (loops) to process data step-by-step.\n\n"
            "It repeatedly executes a block of code until a condition is met.\n\n"
            "This is commonly used for traversal, counting, or repeated operations."
        )

    elif "def" in content_lower:
        return (
            "This appears to be a function definition.\n\n"
            "Functions help in modularizing code and improving reusability.\n\n"
            "The algorithm likely performs a specific task based on input parameters."
        )

    elif "if" in content_lower:
        return (
            "This algorithm uses conditional logic.\n\n"
            "It makes decisions based on conditions, allowing different execution paths.\n\n"
            "Useful for branching logic and rule-based systems."
        )

    elif "sort" in content_lower:
        return (
            "This algorithm seems related to sorting.\n\n"
            "Sorting algorithms arrange elements in a specific order.\n\n"
            "Common examples include Bubble Sort, Merge Sort, and Quick Sort."
        )

    else:
        return (
            "This algorithm processes input data step-by-step.\n\n"
            "It likely follows a structured approach involving input, processing, "
            "and output generation.\n\n"
            "Further analysis can provide more detailed insights."
        )