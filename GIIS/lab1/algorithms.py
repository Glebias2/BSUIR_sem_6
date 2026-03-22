"""
Алгоритмы построения отрезков:
1. ЦДА (Цифровой дифференциальный анализатор)
2. Целочисленный алгоритм Брезенхема
3. Алгоритм Ву (сглаживание)
"""

import math


def _sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


def dda(x1, y1, x2, y2):
    """Алгоритм ЦДА (цифровой дифференциальный анализатор).

    Возвращает dict с ключами:
        points — список (x, y, intensity)
        steps  — список словарей для отладочной таблицы
    """
    points = []
    steps = []

    dx_total = x2 - x1
    dy_total = y2 - y1

    length = max(abs(dx_total), abs(dy_total))

    if length == 0:
        points.append((x1, y1, 1.0))
        steps.append({"i": 0, "x": x1 + 0.5 * _sign(0), "y": y1 + 0.5 * _sign(0),
                       "plot_x": x1, "plot_y": y1})
        return {"points": points, "steps": steps}

    dx = dx_total / length
    dy = dy_total / length

    x = x1 + 0.5 * _sign(dx)
    y = y1 + 0.5 * _sign(dy)

    plot_x, plot_y = int(x), int(y)
    points.append((plot_x, plot_y, 1.0))
    steps.append({"i": 0, "x": round(x, 4), "y": round(y, 4),
                   "plot_x": plot_x, "plot_y": plot_y})

    for i in range(1, length + 1):
        x += dx
        y += dy
        plot_x, plot_y = int(x), int(y)
        points.append((plot_x, plot_y, 1.0))
        steps.append({"i": i, "x": round(x, 4), "y": round(y, 4),
                       "plot_x": plot_x, "plot_y": plot_y})

    return {"points": points, "steps": steps}


def bresenham(x1, y1, x2, y2):
    """Целочисленный алгоритм Брезенхема (обобщённый для всех октантов).

    Возвращает dict с ключами:
        points — список (x, y, intensity)
        steps  — список словарей для отладочной таблицы
    """
    points = []
    steps = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = _sign(x2 - x1)
    sy = _sign(y2 - y1)

    swapped = False
    if dy > dx:
        dx, dy = dy, dx
        swapped = True

    e = 2 * dy - dx
    x, y = x1, y1

    for i in range(dx + 1):
        points.append((x, y, 1.0))
        e_before = e
        steps.append({"i": i, "e": e_before, "x": x, "y": y,
                       "plot_x": x, "plot_y": y})

        if e >= 0:
            if swapped:
                x += sx
            else:
                y += sy
            e -= 2 * dx

        if swapped:
            y += sy
        else:
            x += sx
        e += 2 * dy

    return {"points": points, "steps": steps}


def wu(x1, y1, x2, y2):
    """Алгоритм Ву — построение отрезка со сглаживанием (anti-aliasing).

    Возвращает dict с ключами:
        points — список (x, y, intensity), intensity в [0..1]
        steps  — список словарей для отладочной таблицы
    """
    points = []
    steps = []

    dx = x2 - x1
    dy = y2 - y1

    # Горизонтальные, вертикальные и диагональные — без сглаживания
    if dx == 0 and dy == 0:
        points.append((x1, y1, 1.0))
        steps.append({"i": 0, "x": x1, "y": y1, "intensity": 1.0})
        return {"points": points, "steps": steps}

    steep = abs(dy) > abs(dx)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dx, dy = dy, dx

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        dx, dy = -dx, -dy

    dx = x2 - x1
    dy = y2 - y1
    gradient = dy / dx if dx != 0 else 1.0

    # Первая концевая точка
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xpxl1 = xend
    ypxl1 = int(yend)

    if steep:
        points.append((ypxl1, xpxl1, 1.0))
        points.append((ypxl1 + 1, xpxl1, 0.0))
    else:
        points.append((xpxl1, ypxl1, 1.0))
        points.append((xpxl1, ypxl1 + 1, 0.0))

    intery = yend + gradient

    # Вторая концевая точка
    xend = round(x2)
    yend = y2 + gradient * (xend - x2)
    xpxl2 = xend
    ypxl2 = int(yend)

    if steep:
        points.append((ypxl2, xpxl2, 1.0))
        points.append((ypxl2 + 1, xpxl2, 0.0))
    else:
        points.append((xpxl2, ypxl2, 1.0))
        points.append((xpxl2, ypxl2 + 1, 0.0))

    step_i = 0
    # Основной цикл
    for x in range(xpxl1 + 1, xpxl2):
        frac = intery - int(intery)
        int_y = int(intery)

        i1 = 1.0 - frac
        i2 = frac

        if steep:
            points.append((int_y, x, i1))
            points.append((int_y + 1, x, i2))
            steps.append({"i": step_i, "x": int_y, "y": x,
                           "x2": int_y + 1, "y2": x,
                           "intensity1": round(i1, 4),
                           "intensity2": round(i2, 4)})
        else:
            points.append((x, int_y, i1))
            points.append((x, int_y + 1, i2))
            steps.append({"i": step_i, "x": x, "y": int_y,
                           "x2": x, "y2": int_y + 1,
                           "intensity1": round(i1, 4),
                           "intensity2": round(i2, 4)})

        intery += gradient
        step_i += 1

    # Добавляем шаги для концевых точек в начало
    if steep:
        endpoint_steps = [
            {"i": "start", "x": ypxl1, "y": xpxl1,
             "x2": ypxl1 + 1, "y2": xpxl1,
             "intensity1": 1.0, "intensity2": 0.0},
            {"i": "end", "x": ypxl2, "y": xpxl2,
             "x2": ypxl2 + 1, "y2": xpxl2,
             "intensity1": 1.0, "intensity2": 0.0},
        ]
    else:
        endpoint_steps = [
            {"i": "start", "x": xpxl1, "y": ypxl1,
             "x2": xpxl1, "y2": ypxl1 + 1,
             "intensity1": 1.0, "intensity2": 0.0},
            {"i": "end", "x": xpxl2, "y": ypxl2,
             "x2": xpxl2, "y2": ypxl2 + 1,
             "intensity1": 1.0, "intensity2": 0.0},
        ]
    steps = endpoint_steps + steps

    # Убираем пиксели с нулевой интенсивностью для отрисовки
    points = [(px, py, intensity) for px, py, intensity in points if intensity > 0.001]

    return {"points": points, "steps": steps}
