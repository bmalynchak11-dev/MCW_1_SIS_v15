def view(elements: list[dict], level: str, scope: str | None = None) -> list[str]:
    if level not in {"context", "container", "component"}:
        raise ValueError(f"Невідомий рівень: {level}")

    valid_kinds = {"person", "system", "container", "component"}
    for elem in elements:
        k = elem.get("kind")
        if k not in valid_kinds:
            raise ValueError(f"Невідомий тип елемента: {k}")

    # Валідація scope відповідно до рівня
    if level == "container":
        is_system = any(e.get("name") == scope and e.get("kind") == "system" for e in elements)
        if not is_system:
            raise ValueError(f"Невідомий обсяг: {scope}")
    elif level == "component":
        is_container = any(e.get("name") == scope and e.get("kind") == "container" for e in elements)
        if not is_container:
            raise ValueError(f"Невідомий обсяг: {scope}")

    res = []
    for elem in elements:
        k = elem.get("kind")
        name = elem.get("name")
        parent = elem.get("parent")

        if level == "context":
            if k in {"person", "system"}:
                res.append(name)
        elif level == "container":
            if k == "person":
                res.append(name)
            elif k == "system" and name != scope:
                res.append(name)
            elif k == "container" and parent == scope:
                res.append(name)
        elif level == "component":
            if k in {"person", "system"}:
                res.append(name)
            elif k == "container" and name != scope:
                res.append(name)
            elif k == "component" and parent == scope:
                res.append(name)

    return res