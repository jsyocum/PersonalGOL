'''
Positions within square of 'Scale' width and height
'''

def top_left():
    return top_l

def top_right():
    return (top_left()[0] + Scale, top_left()[1])

def bottom_left():
    return (top_left()[0], top_left()[1] + Scale)

def bottom_right():
    return (top_left()[0] + Scale, top_left()[1] + Scale)


def top_center():
    return (round(top_left()[0] + Scale / 2), top_left()[1])

def bottom_center():
    return (round(top_left()[0] + Scale / 2), top_left()[1] + Scale)

def left_center():
    return (top_left()[0], round(top_left()[1] + Scale / 2))

def right_center():
    return (top_left()[0] + Scale, round(top_left()[1] + Scale / 2))

def center():
    return (round(top_left()[0] + Scale / 2), round(top_left()[1] + Scale / 2))


def top_one_third():
    return (round(top_left()[0] + Scale / 3), top_left()[1])

def top_two_third():
    return (round(top_left()[0] + Scale / 3 * 2), top_left()[1])

def bottom_one_third():
    return (round(top_left()[0] + Scale / 3), top_left()[1] + Scale)

def bottom_two_third():
    return (round(top_left()[0] + Scale / 3 * 2), top_left()[1] + Scale)

def left_one_third():
    return (top_left()[0], round(top_left()[1] + Scale / 3))

def left_two_third():
    return (top_left()[0], round(top_left()[1] + Scale / 3 * 2))

def right_one_third():
    return (top_left()[0] + Scale, round(top_left()[1] + Scale / 3))

def right_two_third():
    return (top_left()[0] + Scale, round(top_left()[1] + Scale / 3 * 2))

def center_one_third_y():
    return (round(top_left()[0] + Scale / 2), round(top_left()[1] + Scale / 3))

def center_two_third_y():
    return (round(top_left()[0] + Scale / 2), round(top_left()[1] + Scale / 3 * 2))

def center_one_third_x():
    return (round(top_left()[0] + Scale / 3), round(top_left()[1] + Scale / 2))

def center_two_third_x():
    return (round(top_left()[0] + Scale / 3 * 2), round(top_left()[1] + Scale / 2))



def get_shape_points(pattern_int, tl, s):
    global top_l, Scale
    top_l, Scale = (round(tl[0]), round(tl[1])), round(s - 1)

    shape_points = []

    match pattern_int:
        case 0:
            # Full square
            shape_points.append(((top_left(), bottom_left(), bottom_right(), top_right()), 'polygon'))

        case 1:
            # 1/2 triangles, bases at bottom left and top right
            shape_points.append(((top_left(), bottom_left(), bottom_right()), 'polygon'))
            shape_points.append(((top_left(), top_right(), bottom_right()), 'polygon'))

        case 2:
            # 1/2 triangle, bases at top left and bottom right
            shape_points.append(((top_left(), top_right(), bottom_left()), 'polygon'))
            shape_points.append(((top_right(), bottom_left(), bottom_right()), 'polygon'))

        case 3:
            # 1/2 rectangles, width > height
            shape_points.append(((top_left(), left_center(), right_center(), top_right()), 'polygon'))
            shape_points.append(((left_center(), bottom_left(), bottom_right(), right_center()), 'polygon'))

        case 4:
            # 1/2 rectangles, width < height
            shape_points.append(((top_left(), bottom_left(), bottom_center(), top_center()), 'polygon'))
            shape_points.append(((top_center(), bottom_center(), bottom_right(), top_right()), 'polygon'))

        case 5:
            # 1/3 triangles, 'teeth' down
            shape_points.append(((top_left(), bottom_left(), top_center()), 'polygon'))
            shape_points.append(((top_right(), bottom_right(), top_center()), 'polygon'))
            shape_points.append(((bottom_left(), bottom_right(), top_center()), 'polygon'))

        case 6:
            # 1/3 triangles, 'teeth' up
            shape_points.append(((top_right(), bottom_right(), bottom_center()), 'polygon'))
            shape_points.append(((top_left(), bottom_left(), bottom_center()), 'polygon'))
            shape_points.append(((top_left(), top_right(), bottom_center()), 'polygon'))

        case 7:
            # 1/3 triangles, 'teeth' left to right
            shape_points.append(((bottom_left(), bottom_right(), left_center()), 'polygon'))
            shape_points.append(((top_left(), top_right(), left_center()), 'polygon'))
            shape_points.append(((top_right(), bottom_right(), left_center()), 'polygon'))

        case 8:
            # 1/3 triangles, 'teeth' right to left
            shape_points.append(((top_left(), top_right(), right_center()), 'polygon'))
            shape_points.append(((bottom_left(), bottom_right(), right_center()), 'polygon'))
            shape_points.append(((top_left(), bottom_left(), right_center()), 'polygon'))

        case 9:
            # 1/4 triangles, meet in the middle
            shape_points.append(((top_left(), top_right(), center()), 'polygon'))
            shape_points.append(((bottom_left(), bottom_right(), center()), 'polygon'))
            shape_points.append(((top_left(), bottom_left(), center()), 'polygon'))
            shape_points.append(((top_right(), bottom_right(), center()), 'polygon'))

        case 10:
            # 1/3 rectangles, equal sizes, width > height
            shape_points.append(((top_left(), left_one_third(), right_one_third(), top_right()), 'polygon'))
            shape_points.append(((left_one_third(), left_two_third(), right_two_third(), right_one_third()), 'polygon'))
            shape_points.append(((left_two_third(), bottom_left(), bottom_right(), right_two_third()), 'polygon'))

        case 11:
            # 1/3 rectangles, equal sizes, width < height
            shape_points.append(((top_left(), bottom_left(), bottom_one_third(), top_one_third()), 'polygon'))
            shape_points.append(((top_one_third(), bottom_one_third(), bottom_two_third(), top_two_third()), 'polygon'))
            shape_points.append(((top_two_third(), bottom_two_third(), bottom_right(), top_right()), 'polygon'))

        case 12:
            # 1/2 square at top, 1/4 squares at bottom
            shape_points.append(((left_center(), bottom_left(), bottom_center(), center()), 'polygon'))
            shape_points.append(((center(), bottom_center(), bottom_right(), right_center()), 'polygon'))
            shape_points.append(((top_left(), left_center(), right_center(), top_right()), 'polygon'))

        case 13:
            # 1/2 square at bottom, 1/4 squares at top
            shape_points.append(((top_center(), center(), right_center(), top_right()), 'polygon'))
            shape_points.append(((top_left(), left_center(), center(), top_center()), 'polygon'))
            shape_points.append(((left_center(), bottom_left(), bottom_right(), right_center()), 'polygon'))

        case 14:
            # 1/2 square at left, 1/4 squares at right
            shape_points.append(((center(), bottom_center(), bottom_right(), right_center()), 'polygon'))
            shape_points.append(((top_center(), center(), right_center(), top_right()), 'polygon'))
            shape_points.append(((top_left(), bottom_left(), bottom_center(), top_center()), 'polygon'))

        case 15:
            # 1/2 square at right, 1/4 squares at left
            shape_points.append(((top_left(), left_center(), center(), top_center()), 'polygon'))
            shape_points.append(((left_center(), bottom_left(), bottom_center(), center()), 'polygon'))
            shape_points.append(((top_center(), bottom_center(), bottom_right(), top_right()), 'polygon'))

        case 16:
            # 1/3 rectangle at top, 2 rectangles at bottom
            shape_points.append(((left_one_third(), bottom_left(), bottom_center(), center_one_third_y()), 'polygon'))
            shape_points.append(((center_one_third_y(), bottom_center(), bottom_right(), right_one_third()), 'polygon'))
            shape_points.append(((top_left(), left_one_third(), right_one_third(), top_right()), 'polygon'))

        case 17:
            # 1/3 rectangle at bottom, 2 rectangles at top
            shape_points.append(((top_center(), center_two_third_y(), right_two_third(), top_right()), 'polygon'))
            shape_points.append(((top_left(), left_two_third(), center_two_third_y(), top_center()), 'polygon'))
            shape_points.append(((left_two_third(), bottom_left(), bottom_right(), right_two_third()), 'polygon'))

        case 18:
            # 1/3 rectangle at left, 2 rectangles at right
            shape_points.append(((center_one_third_x(), bottom_one_third(), bottom_right(), right_center()), 'polygon'))
            shape_points.append(((top_one_third(), center_one_third_x(), right_center(), top_right()), 'polygon'))
            shape_points.append(((top_left(), bottom_left(), bottom_one_third(), top_one_third()), 'polygon'))

        case 19:
            # 1/3 rectangle at right, 2 rectangles at left
            shape_points.append(((top_left(), left_center(), center_two_third_x(), top_two_third()), 'polygon'))
            shape_points.append(((left_center(), bottom_left(), bottom_two_third(), center_two_third_x()), 'polygon'))
            shape_points.append(((top_two_third(), bottom_two_third(), bottom_right(), top_right()), 'polygon'))

    return shape_points

def get_max_patterns():
    return 19

def get_max_shapes():
    return 4
