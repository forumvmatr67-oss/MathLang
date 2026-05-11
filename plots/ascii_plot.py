import math

def plot(func_expr, xmin, xmax, width=60, height=20, char='*'):
    """
    Рисует график функции одной переменной в текстовом виде.
    func_expr: строка с формулой (использует переменную x)
    xmin, xmax: диапазон по X
    width, height: размер в символах
    char: символ для рисования
    """
    # Создаём список значений Y
    xs = [xmin + i * (xmax - xmin) / (width - 1) for i in range(width)]
    ys = []
    for x in xs:
        # Вычисляем выражение: подставляем x вместо 'x'
        # Безопасно через eval с ограниченным пространством имён
        try:
            # Доступные функции: sin, cos, sqrt, log, exp, abs, floor, ceil, pi
            namespace = {
                'x': x,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
                'abs': abs, 'floor': math.floor, 'ceil': math.ceil,
                'pi': math.pi
            }
            y = eval(func_expr, {"__builtins__": {}}, namespace)
            ys.append(y)
        except:
            ys.append(float('nan'))
    
    # Найти min и max Y (игнорируя nan)
    valid_ys = [y for y in ys if not math.isnan(y)]
    if not valid_ys:
        print("Ошибка: нет вычисленных значений")
        return
    ymin = min(valid_ys)
    ymax = max(valid_ys)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    
    # Строим сетку символов
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Отрисовка графика
    for i, y in enumerate(ys):
        if math.isnan(y):
            continue
        # Нормализация Y в диапазон [0, height-1]
        y_norm = int((y - ymin) / (ymax - ymin) * (height - 1))
        y_norm = max(0, min(height - 1, y_norm))
        grid[height - 1 - y_norm][i] = char
    
    # Отрисовка осей
    # Горизонтальная ось (y=0)
    zero_row = None
    if ymin <= 0 <= ymax:
        zero_row = int((0 - ymin) / (ymax - ymin) * (height - 1))
        zero_row = height - 1 - zero_row
        for i in range(width):
            if grid[zero_row][i] == ' ':
                grid[zero_row][i] = '-'
    
    # Вертикальная ось (x=0)
    zero_col = None
    if xmin <= 0 <= xmax:
        zero_col = int((0 - xmin) / (xmax - xmin) * (width - 1))
        for j in range(height):
            if grid[j][zero_col] == ' ':
                grid[j][zero_col] = '|'
    
    # Пересечение осей
    if zero_row is not None and zero_col is not None:
        if grid[zero_row][zero_col] == '-':
            grid[zero_row][zero_col] = '+'
        elif grid[zero_row][zero_col] == '|':
            grid[zero_row][zero_col] = '+'
    
    # Печать результата
    print(f"График функции: {func_expr}")
    print(f"Диапазон X: [{xmin}, {xmax}], Y: [{ymin:.3f}, {ymax:.3f}]")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")

def scatter(x_list, y_list, width=60, height=20, char='o'):
    """
    Рисует точечную диаграмму по спискам точек.
    x_list, y_list: списки чисел (одинаковой длины)
    """
    if len(x_list) != len(y_list):
        print("Ошибка: списки X и Y разной длины")
        return
    
    xs = list(x_list)
    ys = list(y_list)
    if not xs:
        return
    
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmin -= 1
        xmax += 1
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    for x, y in zip(xs, ys):
        i = int((x - xmin) / (xmax - xmin) * (width - 1))
        j = int((y - ymin) / (ymax - ymin) * (height - 1))
        i = max(0, min(width - 1, i))
        j = max(0, min(height - 1, j))
        grid[height - 1 - j][i] = char
    
    # Отрисовка осей (упрощённо)
    print(f"Точечная диаграмма, {len(xs)} точек")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")

def grid():
    """Показывает координатную сетку без данных (для справки)"""
    print("Coord system ready. Use plot('x^2', -3, 3)")

def axis():
    """Печатает легенду осей"""
    print("Ось X → горизонталь, ось Y → вертикаль")
