def check_history(history: list[str]) -> str:
    if not history:
        return "Помилка: історія порожня"

    valid_states = {"запропоновано", "прийнято", "відхилено", "застаріло", "замінено"}
    terminal_states = {"відхилено", "застаріло", "замінено"}
    allowed_transitions = {
        ("запропоновано", "запропоновано"),
        ("запропоновано", "прийнято"),
        ("запропоновано", "відхилено"),
        ("прийнято", "застаріло"),
        ("прийнято", "замінено"),
    }

    # 1. Перевірка коректності назв станів
    for i, state in enumerate(history, 1):
        if state not in valid_states:
            return f"Помилка: невідомий стан «{state}» на кроці {i}"

    # 2. Перевірка початкового стану
    if history[0] != "запропоновано":
        return "Помилка: початковий стан має бути «запропоновано»"

    # 3. Перевірка допустимості переходів (зі стрілкою ->)
    for i in range(1, len(history)):
        prev_state = history[i - 1]
        curr_state = history[i]
        if (prev_state, curr_state) not in allowed_transitions:
            return f"Помилка: крок {i + 1}: перехід {prev_state} -> {curr_state} заборонений"

    last_state = history[-1]
    if last_state in terminal_states:
        return f"Історія коректна, поточний стан: {last_state} (кінцевий)"
    return f"Історія коректна, поточний стан: {last_state}"