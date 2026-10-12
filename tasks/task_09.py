def validate_model(model: dict) -> list[str]:
    problems = []
    scope = model.get("scope")
    systems = model.get("systems", [])
    people = model.get("people", [])
    containers = model.get("containers", [])
    relations = model.get("relations", [])

    # 1. Перевірка scope
    scope_sys = next((s for s in systems if s.get("id") == scope), None)
    if not scope_sys or scope_sys.get("external") is True:
        problems.append(f"Невідомий обсяг: {scope}")

    # 2. Не зовнішні системи, крім scope
    for s in systems:
        if s.get("id") != scope and not s.get("external", False):
            problems.append(f"Система {s.get('id')}: має бути зовнішньою")

    # 3. Наявність контейнерів
    if not containers:
        problems.append("У системі немає контейнерів")

    # 4. Повтор ідентифікатора
    seen_ids = set()
    for entity_list in [people, systems, containers]:
        for e in entity_list:
            eid = e.get("id")
            if eid in seen_ids:
                problems.append(f"Дубль ідентифікатора: {eid}")
            else:
                seen_ids.add(eid)

    # 5. Валідація контейнерів
    for c in containers:
        cid = c.get("id")
        kind = c.get("kind", "app")
        if kind not in {"app", "database"}:
            problems.append(f"Контейнер {cid}: невідомий вид {kind}")
        tech = c.get("technology")
        if tech is None or not str(tech).strip():
            problems.append(f"Контейнер {cid}: немає технології")

    all_elements = {}
    for p in people:
        all_elements[p["id"]] = ("person", p)
    for s in systems:
        all_elements[s["id"]] = ("system", s)
    for c in containers:
        all_elements[c["id"]] = ("container", c)

    # 6. Валідація зв'язків
    for idx, rel in enumerate(relations, 1):
        f = rel.get("from")
        t = rel.get("to")

        if f not in all_elements:
            problems.append(f"Зв'язок {idx}: невідомий елемент {f}")
            continue
        if t not in all_elements:
            problems.append(f"Зв'язок {idx}: невідомий елемент {t}")
            continue

        if f == t:
            problems.append(f"Зв'язок {idx}: елемент з'єднано сам із собою")
            continue

        desc = rel.get("description")
        if desc is None or not str(desc).strip():
            problems.append(f"Зв'язок {idx}: немає опису")
            continue

        f_type, f_data = all_elements[f]
        t_type, t_data = all_elements[t]
        tech = rel.get("technology")

        if (f_type == "container" or t_type == "container") and (tech is None or not str(tech).strip()):
            problems.append(f"Зв'язок {idx}: немає технології")
            continue

        f_is_db = (f_type == "container" and f_data.get("kind") == "database")
        t_is_db = (t_type == "container" and t_data.get("kind") == "database")

        if f_is_db or t_is_db:
            other_type, other_data = (t_type, t_data) if f_is_db else (f_type, f_data)
            if not (other_type == "container" and other_data.get("kind", "app") == "app"):
                problems.append(f"Зв'язок {idx}: база даних доступна не лише з контейнерів")
                continue

    # 7. Елементи без жодного зв'язку
    connected_ids = set()
    for rel in relations:
        f = rel.get("from")
        t = rel.get("to")
        if f in all_elements and t in all_elements:
            connected_ids.add(f)
            connected_ids.add(t)

    for entity_list in [people, systems, containers]:
        for e in entity_list:
            eid = e.get("id")
            if eid != scope and eid not in connected_ids:
                problems.append(f"Елемент {eid}: немає жодного зв'язку")

    return problems


def to_mermaid(model: dict) -> str:
    problems = validate_model(model)
    if problems:
        raise ValueError(f"Модель містить помилки: {len(problems)}")

    def clean(val):
        return str(val).replace('"', "'") if val is not None else ""

    lines = ["C4Container", f"    title {clean(model.get('title'))}"]

    for p in model.get("people", []):
        pid = clean(p.get("id"))
        pname = clean(p.get("name"))
        desc = p.get("description")
        if desc is not None and str(desc).strip():
            lines.append(f'    Person({pid}, "{pname}", "{clean(desc)}")')
        else:
            lines.append(f'    Person({pid}, "{pname}")')

    for s in model.get("systems", []):
        if s.get("external", False):
            sid = clean(s.get("id"))
            sname = clean(s.get("name"))
            desc = s.get("description")
            if desc is not None and str(desc).strip():
                lines.append(f'    System_Ext({sid}, "{sname}", "{clean(desc)}")')
            else:
                lines.append(f'    System_Ext({sid}, "{sname}")')

    scope_id = model.get("scope")
    scope_sys = next(s for s in model["systems"] if s.get("id") == scope_id)
    scope_name = clean(scope_sys.get("name"))

    lines.append(f'    System_Boundary({scope_id}, "{scope_name}") {{')
    for c in model.get("containers", []):
        macro = "ContainerDb" if c.get("kind") == "database" else "Container"
        cid = clean(c.get("id"))
        cname = clean(c.get("name"))
        ctech = clean(c.get("technology"))
        desc = c.get("description")
        if desc is not None and str(desc).strip():
            lines.append(f'        {macro}({cid}, "{cname}", "{ctech}", "{clean(desc)}")')
        else:
            lines.append(f'        {macro}({cid}, "{cname}", "{ctech}")')
    lines.append("    }")

    for r in model.get("relations", []):
        f = clean(r.get("from"))
        t = clean(r.get("to"))
        desc = clean(r.get("description"))
        tech = r.get("technology")
        if tech is not None and str(tech).strip():
            lines.append(f'    Rel({f}, {t}, "{desc}", "{clean(tech)}")')
        else:
            lines.append(f'    Rel({f}, {t}, "{desc}")')

    return "\n".join(lines)