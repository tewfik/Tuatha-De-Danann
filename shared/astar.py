#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt

def lowest(lst):
    """
    """
    low = lst[0]
    for elt in lst:
        if elt[3] < low[3]:
            low = elt
    return low

def remove(elt, lst):
    """
    """
    for i in xrange(len(lst)):
        if lst[i][0] == elt[0] and lst[i][1] == elt[1]:
            lst.pop(i)
            break

def notin(elt, lst):
    """
    """
    result = True
    for i in lst:
        if i[0:2] == elt:
            result = False
            break
    return result

def get(elt, lst):
    """
    """
    result = None
    for i in lst:
        if i[0] == elt[0] and i[1] == elt[1]:
            result = i
            break
    return result

def Astar(map, pos, dest, free, block):
    """
    """
    row = len(map)
    column = len(map[0])
    open = [[pos[0], pos[1], None, 0, 0, 0]]
    close = []

    loop = True
    while loop:
        if len(open) > 0:
            current = lowest(open)
        else:
            break
        remove(current, open)
        close.append(current)
        if current[0] == dest[0] and current[1] == dest[1]:
            loop = False
            break

        # UP
        x = current[0]
        y = current[1] - 1
        if y >= 0:
            square = [x, y]
            if map[y][x] not in block and notin(square, close):
                G = current[4] + 1
                H = sqrt((x - dest[0])**2 + (y - dest[1])**2)
                F = G + H
                if notin(square, open):
                    square += [current, F, G, H]
                    open.append(square)
                else:
                    square = get(square, open)
                    if G < square[4]:
                        square[4] = G
                        square[3] = F
                        square[2] = current

        # RIGHT
        x = current[0] + 1
        y = current[1]
        if x < column:
            square = [x, y]
            if map[y][x] not in block and notin(square, close):
                G = current[4] + 1
                H = sqrt((x - dest[0])**2 + (y - dest[1])**2)
                F = G + H
                if notin(square, open):
                    square += [current, F, G, H]
                    open.append(square)
                else:
                    square = get(square, open)
                    if G < square[4]:
                        square[4] = G
                        square[3] = F
                        square[2] = current

        # DOWN
        x = current[0]
        y = current[1] + 1
        if y < row:
            square = [x, y]
            if map[y][x] not in block and notin(square, close):
                G = current[4] + 1
                H = sqrt((x - dest[0])**2 + (y - dest[1])**2)
                F = G + H
                if notin(square, open):
                    square += [current, F, G, H]
                    open.append(square)
                else:
                    square = get(square, open)
                    if G < square[4]:
                        square[4] = G
                        square[3] = F
                        square[2] = current

        # LEFT
        x = current[0] - 1
        y = current[1]
        if x >= 0:
            square = [x, y]
            if map[y][x] not in block and notin(square, close):
                G = current[4] + 1
                H = sqrt((x - dest[0])**2 + (y - dest[1])**2)
                F = G + H
                if notin(square, open):
                    square += [current, F, G, H]
                    open.append(square)
                else:
                    square = get(square, open)
                    if G < square[4]:
                        square[4] = G
                        square[3] = F
                        square[2] = current


    if loop == True:
        return None
    else:
        square = get(dest, close)
        path = [(square[0], square[1])]
        while True:
            square = square[2]
            if square[2] is None:
                break
            path.insert(0, (square[0], square[1]))
        return path
