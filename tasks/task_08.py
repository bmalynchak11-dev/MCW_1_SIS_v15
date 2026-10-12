def decide(options: dict, criteria: dict, constraints: list) -> str:
    # 1. Сума ваг має дорівнювати 1
    total_weight = sum(c["weight"] for c in criteria.values())
    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError("Сума ваг має дорівнювати 1")

    # 2. Недопустимий напрям критерію
    for crit_name, crit_data in criteria.items():
        direct = crit_data.get("direction")
        if direct not in {"max", "min"}:
            raise ValueError(f"Некоректний напрям: {direct}")

    # 3. Обмеження з невідомим критерієм
    for crit, op, thresh in constraints:
        if crit not in criteria:
            raise ValueError(f"Невідомий критерій: {crit}")

    # 4. Невідома операція обмеження
    for crit, op, thresh in constraints:
        if op not in {"<=", ">="}:
            raise ValueError(f"Некоректна операція: {op}")

    # 5. У варіанта відсутнє значення критерію
    for opt_name, opt_values in options.items():
        for crit_name in criteria:
            if crit_name not in opt_values:
                raise ValueError(f"Немає значення: {opt_name}.{crit_name}")

    # Фільтрація варіантів за жорсткими обмеженнями
    disqualified = []
    admissible = []

    for opt_name, opt_values in options.items():
        violation = None
        for crit, op, thresh in constraints:
            val = opt_values[crit]
            if op == "<=" and val > thresh:
                violation = (crit, op, thresh)
                break
            elif op == ">=" and val < thresh:
                violation = (crit, op, thresh)
                break

        if violation:
            disqualified.append((opt_name, violation))
        else:
            admissible.append(opt_name)

    lines = []
    for opt_name, (crit, op, thresh) in disqualified:
        lines.append(f"Відсічено: {opt_name} ({crit} {op} {thresh})")

    if not admissible:
        lines.append("Рішення: немає допустимих варіантів")
        return "\n".join(lines)

    # Розрахунок мінімумів і максимумів для нормалізації
    crit_min_max = {}
    for crit_name in criteria:
        vals = [options[opt][crit_name] for opt in admissible]
        crit_min_max[crit_name] = (min(vals), max(vals))

    scores = {}
    for opt_name in admissible:
        score = 0.0
        for crit_name, crit_data in criteria.items():
            w = crit_data["weight"]
            d = crit_data["direction"]
            v = options[opt_name][crit_name]
            mn, mx = crit_min_max[crit_name]

            if mx == mn:
                norm = 1.0
            else:
                if d == "max":
                    norm = (v - mn) / (mx - mn)
                else:
                    norm = (mx - v) / (mx - mn)
            score += w * norm
        scores[opt_name] = score

    lines.append("Оцінки:")
    opt_indices = {name: i for i, name in enumerate(options.keys())}
    # Збіг оцінок до 9 знаків вважається рівним
    sorted_opts = sorted(
        admissible,
        key=lambda name: (-round(scores[name], 9), opt_indices[name])
    )

    for opt in sorted_opts:
        lines.append(f"{opt}: {scores[opt]:.3f}")

    winner = sorted_opts[0]
    lines.append(f"Рішення: {winner}")

    if len(sorted_opts) > 1:
        diff = scores[winner] - scores[sorted_opts[1]]
        if diff < 0:
            diff = 0.0
        lines.append(f"Відрив від другого: {diff:.3f}")
    else:
        lines.append("Відрив від другого: немає")

    return "\n".join(lines)