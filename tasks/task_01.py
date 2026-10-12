def select_drivers(requirements: list[dict]) -> list[str]:
    valid_kinds = {"functional", "quality", "constraint", "business"}
    valid_levels = {"high", "medium", "low"}

    # Перевірка валідності полів
    for req in requirements:
        kind = req.get("kind")
        if kind not in valid_kinds:
            raise ValueError(f"Некоректне значення поля kind: {kind}")
        
        importance = req.get("importance")
        if importance not in valid_levels:
            raise ValueError(f"Некоректне значення поля importance: {importance}")
        
        difficulty = req.get("difficulty")
        if difficulty not in valid_levels:
            raise ValueError(f"Некоректне значення поля difficulty: {difficulty}")

    # Відбір драйверів: importance == 'high' та (difficulty != 'low' або kind == 'constraint')
    drivers = []
    for req in requirements:
        if req["importance"] == "high":
            if req["difficulty"] != "low" or req["kind"] == "constraint":
                drivers.append(req)

    # Сортування: high -> medium -> low зі збереженням вихідного порядку
    order = {"high": 0, "medium": 1, "low": 2}
    sorted_drivers = sorted(drivers, key=lambda r: order[r["difficulty"]])

    return [r["id"] for r in sorted_drivers]