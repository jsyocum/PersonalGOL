'''
Positions within square of 'Scale' width and height
'''

def gp(x_fraction, y_fraction):
    return (round(top_l[0] + Scale * x_fraction), round(top_l[1] + Scale * y_fraction))

def get_shape_points(pattern_type, pattern_int, tl, s):
    global top_l, Scale
    top_l, Scale = (round(tl[0]), round(tl[1])), round(s - 1)

    shape_points = []

    match pattern_type:

        case 'Rectangles':
            match pattern_int:
                case 0:
                    # Full square
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 1:
                    # 1/2 rectangles, width > height
                    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

                case 2:
                    # 1/2 rectangles, width < height
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 3:
                    # 1/3 rectangles, equal sizes, width > height
                    shape_points.append(((gp(0, 0), gp(0, 1 / 3), gp(1, 1 / 3), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'polygon'))
                    shape_points.append(((gp(0, 2 / 3), gp(0, 1), gp(1, 1), gp(1, 2 / 3)), 'polygon'))

                case 4:
                    # 1/3 rectangles, equal sizes, width < height
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 3, 1), gp(1 / 3, 0)), 'polygon'))
                    shape_points.append(((gp(1 / 3, 0), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 0)), 'polygon'))
                    shape_points.append(((gp(2 / 3, 0), gp(2 / 3, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 5:
                    # 1/2 square at top, 1/4 squares at bottom
                    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))

                case 6:
                    # 1/2 square at bottom, 1/4 squares at top
                    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

                case 7:
                    # 1/2 square at left, 1/4 squares at right
                    shape_points.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 0)), 'polygon'))

                case 8:
                    # 1/2 square at right, 1/4 squares at left
                    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 9:
                    # 1/3 rectangle at top, 2 rectangles at bottom
                    shape_points.append(((gp(0, 1 / 3), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 3)), 'polygon'))
                    shape_points.append(((gp(1 / 2, 1 / 3), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 3)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1 / 3), gp(1, 1 / 3), gp(1, 0)), 'polygon'))

                case 10:
                    # 1/3 rectangle at bottom, 2 rectangles at top
                    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 2 / 3), gp(1, 2 / 3), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 2 / 3), gp(1 / 2, 2 / 3), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(0, 2 / 3), gp(0, 1), gp(1, 1), gp(1, 2 / 3)), 'polygon'))

                case 11:
                    # 1/3 rectangle at left, 2 rectangles at right
                    shape_points.append(((gp(1 / 3, 1 / 2), gp(1 / 3, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1 / 3, 0), gp(1 / 3, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 3, 1), gp(1 / 3, 0)), 'polygon'))

                case 12:
                    # 1/3 rectangle at right, 2 rectangles at left
                    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(2 / 3, 1 / 2), gp(2 / 3, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(2 / 3, 1), gp(2 / 3, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(2 / 3, 0), gp(2 / 3, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 13:
                    # Diamond in the middle with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(1 / 2, 0), gp(0, 1 / 2), gp(1 / 2, 1), gp(1, 1 / 2)), 'polygon'))


        case 'Triangles':
            match pattern_int:
                case 0:
                    # 1/2 triangles, bases at bottom left and top right
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1, 1)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(1, 1)), 'polygon'))

                case 1:
                    # 1/2 triangle, bases at top left and bottom right
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(0, 1)), 'polygon'))
                    shape_points.append(((gp(1, 0), gp(0, 1), gp(1, 1)), 'polygon'))

                case 2:
                    # 1/3 triangles, 'teeth' down
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 0)), 'polygon'))
                    shape_points.append(((gp(0, 1), gp(1, 1), gp(1 / 2, 0)), 'polygon'))

                case 3:
                    # 1/3 triangles, 'teeth' up
                    shape_points.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 1)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(1 / 2, 1)), 'polygon'))

                case 4:
                    # 1/3 triangles, 'teeth' left to right
                    shape_points.append(((gp(0, 1), gp(1, 1), gp(0, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(0, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1, 0), gp(1, 1), gp(0, 1 / 2)), 'polygon'))

                case 5:
                    # 1/3 triangles, 'teeth' right to left
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(1, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1, 1 / 2)), 'polygon'))

                case 6:
                    # 1/4 triangles, meet in the middle
                    shape_points.append(((gp(0, 0), gp(1, 0), gp(1 / 2, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 1), gp(1, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    shape_points.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 1 / 2)), 'polygon'))


        case 'Ellipses':
            match pattern_int:
                case 0:
                    # Circle with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(0, 0), gp(0, 1), gp(1, 1), gp(1, 0)), 'ellipse'))

                case 1:
                    # Horizontal ellipse with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'ellipse'))

                case 2:
                    # Vertical ellipse with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(1 / 3, 0), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 0)), 'ellipse'))

                case 3:
                    # Bottom left to top right diagonal ellipse with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(0, 2 / 3), gp(1 / 3, 1), gp(1, 1 / 3), gp(2 / 3, 0)), 'ellipse'))

                case 4:
                    # Top left to bottom right diagonal ellipse with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(1 / 3, 0), gp(0, 1 / 3), gp(2 / 3, 1), gp(1, 2 / 3)), 'ellipse'))

                case 5:
                    # Smaller centered circle with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(1 / 3, 1 / 3), gp(1 / 3, 2 / 3), gp(2 / 3, 2 / 3), gp(2 / 3, 1 / 3)), 'ellipse'))

                case 6:
                    # Four ellipses pointing to the center with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(1 / 3, 0), gp(1 / 3, 1 / 2), gp(2 / 3, 1 / 2), gp(2 / 3, 0)), 'ellipse'))
                    shape_points.append(((gp(1 / 2, 1 / 3), gp(1 / 2, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'ellipse'))
                    shape_points.append(((gp(1 / 3, 1 / 2), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 1 / 2)), 'ellipse'))
                    shape_points.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1 / 2, 2 / 3), gp(1 / 2, 1 / 3)), 'ellipse'))

                case 7:
                    # Four diagonal ellipses pointing to the center with colorable corners
                    create_colorable_corners(shape_points)
                    shape_points.append(((gp(0, 1 / 6), gp(1 / 3, 1 / 2), gp(1 / 2, 1 / 3), gp(1 / 6, 0)), 'ellipse'))
                    shape_points.append(((gp(1 / 2, 1 / 3), gp(2 / 3, 1 / 2), gp(1, 1 / 6), gp(5 / 6, 0)), 'ellipse'))
                    shape_points.append(((gp(1 / 2, 2 / 3), gp(5 / 6, 1), gp(1, 5 / 6), gp(2 / 3, 1 / 2)), 'ellipse'))
                    shape_points.append(((gp(0, 5 / 6), gp(1 / 6, 1), gp(1 / 2, 2 / 3), gp(1 / 3, 1 / 2)), 'ellipse'))


    return shape_points

# Adds four squares to a pattern
def create_colorable_corners(shape_points):
    shape_points.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
    shape_points.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
    shape_points.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
    shape_points.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

def get_pattern_types():
    return ['Rectangles', 'Triangles', 'Ellipses'], 3

def get_max_patterns(pattern_type):
    match pattern_type:
        case 'Rectangles':
            return 13

        case 'Triangles':
            return 6

        case 'Ellipses':
            return 7

    return 0

def get_max_shapes():
    return 8
