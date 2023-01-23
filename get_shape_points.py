'''
Positions within square of 'Scale' width and height
'''

def gp(x_fraction, y_fraction):
    return (round(top_l[0] + Scale * x_fraction), round(top_l[1] + Scale * y_fraction))

def get_shape_points(pattern_type, pattern_int, tl, s):
    global top_l, Scale
    top_l = (round(tl[0]), round(tl[1]))
    Scale = round(s - 1)

    sp = []

    match pattern_type:

        case 'Rectangles':
            match pattern_int:
                case 0:
                    # Full square
                    sp.append(((gp(0, 0), gp(0, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 1:
                    # 1/2 rectangles, width > height
                    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

                case 2:
                    # 1/2 rectangles, width < height
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(1 / 2, 0), gp(1 / 2, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 3:
                    # 1/3 rectangles, equal sizes, width > height
                    sp.append(((gp(0, 0), gp(0, 1 / 3), gp(1, 1 / 3), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'polygon'))
                    sp.append(((gp(0, 2 / 3), gp(0, 1), gp(1, 1), gp(1, 2 / 3)), 'polygon'))

                case 4:
                    # 1/3 rectangles, equal sizes, width < height
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 3, 1), gp(1 / 3, 0)), 'polygon'))
                    sp.append(((gp(1 / 3, 0), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 0)), 'polygon'))
                    sp.append(((gp(2 / 3, 0), gp(2 / 3, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 5:
                    # 1/2 square at top, 1/4 squares at bottom
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    sp.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))

                case 6:
                    # 1/2 square at bottom, 1/4 squares at top
                    sp.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

                case 7:
                    # 1/2 square at left, 1/4 squares at right
                    sp.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    sp.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 0)), 'polygon'))

                case 8:
                    # 1/2 square at right, 1/4 squares at left
                    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    sp.append(((gp(1 / 2, 0), gp(1 / 2, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 9:
                    # 1/3 rectangle at top, 2 rectangles at bottom
                    sp.append(((gp(0, 1 / 3), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 3)), 'polygon'))
                    sp.append(((gp(1 / 2, 1 / 3), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 3)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1 / 3), gp(1, 1 / 3), gp(1, 0)), 'polygon'))

                case 10:
                    # 1/3 rectangle at bottom, 2 rectangles at top
                    sp.append(((gp(1 / 2, 0), gp(1 / 2, 2 / 3), gp(1, 2 / 3), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 2 / 3), gp(1 / 2, 2 / 3), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(0, 2 / 3), gp(0, 1), gp(1, 1), gp(1, 2 / 3)), 'polygon'))

                case 11:
                    # 1/3 rectangle at left, 2 rectangles at right
                    sp.append(((gp(1 / 3, 1 / 2), gp(1 / 3, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    sp.append(((gp(1 / 3, 0), gp(1 / 3, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 3, 1), gp(1 / 3, 0)), 'polygon'))

                case 12:
                    # 1/3 rectangle at right, 2 rectangles at left
                    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(2 / 3, 1 / 2), gp(2 / 3, 0)), 'polygon'))
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(2 / 3, 1), gp(2 / 3, 1 / 2)), 'polygon'))
                    sp.append(((gp(2 / 3, 0), gp(2 / 3, 1), gp(1, 1), gp(1, 0)), 'polygon'))

                case 13:
                    # Diamond in the middle with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(1 / 2, 0), gp(0, 1 / 2), gp(1 / 2, 1), gp(1, 1 / 2)), 'polygon'))


        case 'Triangles':
            match pattern_int:
                case 0:
                    # 1/2 triangles, bases at bottom left and top right
                    sp.append(((gp(0, 0), gp(0, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1, 0), gp(1, 1)), 'polygon'))

                case 1:
                    # 1/2 triangle, bases at top left and bottom right
                    sp.append(((gp(0, 0), gp(1, 0), gp(0, 1)), 'polygon'))
                    sp.append(((gp(1, 0), gp(0, 1), gp(1, 1)), 'polygon'))

                case 2:
                    # 1/3 triangles, 'teeth' down
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 0)), 'polygon'))
                    sp.append(((gp(0, 1), gp(1, 1), gp(1 / 2, 0)), 'polygon'))

                case 3:
                    # 1/3 triangles, 'teeth' up
                    sp.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1, 0), gp(1 / 2, 1)), 'polygon'))

                case 4:
                    # 1/3 triangles, 'teeth' left to right
                    sp.append(((gp(0, 1), gp(1, 1), gp(0, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1, 0), gp(0, 1 / 2)), 'polygon'))
                    sp.append(((gp(1, 0), gp(1, 1), gp(0, 1 / 2)), 'polygon'))

                case 5:
                    # 1/3 triangles, 'teeth' right to left
                    sp.append(((gp(0, 0), gp(1, 0), gp(1, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1), gp(1, 1 / 2)), 'polygon'))

                case 6:
                    # 1/4 triangles, meet in the middle
                    sp.append(((gp(0, 0), gp(1, 0), gp(1 / 2, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 1), gp(1, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    sp.append(((gp(0, 0), gp(0, 1), gp(1 / 2, 1 / 2)), 'polygon'))
                    sp.append(((gp(1, 0), gp(1, 1), gp(1 / 2, 1 / 2)), 'polygon'))

                case 7:
                    # 4 diagonal stripes, going from top left to bottom right
                    sp.append(((gp(0, 0), gp(0, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1, 0), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1)), 'polygon'))
                    sp.append(((gp(1 / 2, 0), gp(1, 0), gp(1, 1 / 2)), 'polygon'))

                case 8:
                    # 4 diagonal stripes, going from top right to bottom left
                    sp.append(((gp(1, 0), gp(0, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1, 0), gp(0, 1)), 'polygon'))
                    sp.append(((gp(1, 1 / 2), gp(1 / 2, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(1 / 2, 0), gp(0, 1 / 2)), 'polygon'))

                case 9:
                    # 4 diagonal stripes, going from top left to bottom right
                    sp.append(((gp(0, 0), gp(1, 0), gp(1, 1), gp(0, 1)), 'polygon'))
                    sp.append(((gp(0, 1 / 5), gp(0, 1), gp(4 / 5, 1)), 'polygon'))
                    sp.append(((gp(1 / 5, 0), gp(1, 0), gp(1, 4 / 5)), 'polygon'))
                    sp.append(((gp(0, 3 / 5), gp(0, 1), gp(2 / 5, 1)), 'polygon'))
                    sp.append(((gp(3 / 5, 0), gp(1, 0), gp(1, 2 / 5)), 'polygon'))

                case 10:
                    # 5 diagonal stripes, going from top right to bottom left
                    sp.append(((gp(0, 0), gp(1, 0), gp(1, 1), gp(0, 1)), 'polygon'))
                    sp.append(((gp(1, 1 / 5), gp(1 / 5, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(4 / 5, 0), gp(0, 4 / 5)), 'polygon'))
                    sp.append(((gp(1, 3 / 5), gp(3 / 5, 1), gp(1, 1)), 'polygon'))
                    sp.append(((gp(0, 0), gp(2 / 5, 0), gp(0, 2 / 5)), 'polygon'))


        case 'Ellipses':
            match pattern_int:
                case 0:
                    # Circle with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(0, 0), gp(0, 1), gp(1, 1), gp(1, 0)), 'ellipse'))

                case 1:
                    # Horizontal ellipse with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'ellipse'))

                case 2:
                    # Vertical ellipse with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(1 / 3, 0), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 0)), 'ellipse'))

                case 3:
                    # Bottom left to top right diagonal ellipse with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(0, 2 / 3), gp(1 / 3, 1), gp(1, 1 / 3), gp(2 / 3, 0)), 'ellipse'))

                case 4:
                    # Top left to bottom right diagonal ellipse with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(1 / 3, 0), gp(0, 1 / 3), gp(2 / 3, 1), gp(1, 2 / 3)), 'ellipse'))

                case 5:
                    # Smaller centered circle with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(1 / 3, 1 / 3), gp(1 / 3, 2 / 3), gp(2 / 3, 2 / 3), gp(2 / 3, 1 / 3)), 'ellipse'))

                case 6:
                    # Four ellipses pointing to the center with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(1 / 3, 0), gp(1 / 3, 1 / 2), gp(2 / 3, 1 / 2), gp(2 / 3, 0)), 'ellipse'))
                    sp.append(((gp(1 / 2, 1 / 3), gp(1 / 2, 2 / 3), gp(1, 2 / 3), gp(1, 1 / 3)), 'ellipse'))
                    sp.append(((gp(1 / 3, 1 / 2), gp(1 / 3, 1), gp(2 / 3, 1), gp(2 / 3, 1 / 2)), 'ellipse'))
                    sp.append(((gp(0, 1 / 3), gp(0, 2 / 3), gp(1 / 2, 2 / 3), gp(1 / 2, 1 / 3)), 'ellipse'))

                case 7:
                    # Four diagonal ellipses pointing to the center with colorable corners
                    create_colorable_corners(sp)
                    sp.append(((gp(0, 1 / 6), gp(1 / 3, 1 / 2), gp(1 / 2, 1 / 3), gp(1 / 6, 0)), 'ellipse'))
                    sp.append(((gp(1 / 2, 1 / 3), gp(2 / 3, 1 / 2), gp(1, 1 / 6), gp(5 / 6, 0)), 'ellipse'))
                    sp.append(((gp(1 / 2, 2 / 3), gp(5 / 6, 1), gp(1, 5 / 6), gp(2 / 3, 1 / 2)), 'ellipse'))
                    sp.append(((gp(0, 5 / 6), gp(1 / 6, 1), gp(1 / 2, 2 / 3), gp(1 / 3, 1 / 2)), 'ellipse'))


    return sp

# Adds four squares to a pattern
def create_colorable_corners(sp):
    sp.append(((gp(0, 0), gp(0, 1 / 2), gp(1 / 2, 1 / 2), gp(1 / 2, 0)), 'polygon'))
    sp.append(((gp(1 / 2, 0), gp(1 / 2, 1 / 2), gp(1, 1 / 2), gp(1, 0)), 'polygon'))
    sp.append(((gp(0, 1 / 2), gp(0, 1), gp(1 / 2, 1), gp(1 / 2, 1 / 2)), 'polygon'))
    sp.append(((gp(1 / 2, 1 / 2), gp(1 / 2, 1), gp(1, 1), gp(1, 1 / 2)), 'polygon'))

def get_pattern_types():
    return ['Rectangles', 'Triangles', 'Ellipses'], 3

def get_max_patterns(pattern_type):
    match pattern_type:
        case 'Rectangles':
            return 13

        case 'Triangles':
            return 10

        case 'Ellipses':
            return 7

    return 0

def get_max_shapes():
    return 8
