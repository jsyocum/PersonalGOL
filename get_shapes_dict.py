def position_shape(shape, top_left):
    if shape[1] is True:
        positioned_shape = (((shape[0][0][0] + top_left[0], shape[0][0][1] + top_left[1]), (shape[0][1][0], shape[0][1][1])), True)
    else:
        poly_tuple = shape[0]
        positioned_poly_array = []
        for pos in poly_tuple:
            positioned_poly_array.append((pos[0] + top_left[0], pos[1] + top_left[1]))

        positioned_poly_tuple = tuple(positioned_poly_array)
        positioned_shape = (positioned_poly_tuple, False)

    return positioned_shape

def get_shapes_dict(Scale, board):
    top_left = (0, 0)
    top_right = (top_left[0] + Scale, top_left[1])
    bottom_left = (top_left[0], top_left[1] + Scale)
    bottom_right = (top_left[0] + Scale, top_left[1] + Scale)

    top_center = (top_left[0] + Scale / 2, top_left[1])
    bottom_center = (top_left[0] + Scale / 2, top_left[1] + Scale)
    left_center = (top_left[0], top_left[1] + Scale / 2)
    right_center = (top_left[0] + Scale, top_left[1] + Scale / 2)
    center = (top_left[0] + Scale / 2, top_left[1] + Scale / 2)

    top_one_third = (top_left[0] + Scale / 3, top_left[1])
    top_two_third = (top_left[0] + Scale / 3 * 2, top_left[1])
    bottom_one_third = (top_left[0] + Scale / 3, top_left[1] + Scale)
    bottom_two_third = (top_left[0] + Scale / 3 * 2, top_left[1] + Scale)
    left_one_third = (top_left[0], top_left[1] + Scale / 3)
    left_two_third = (top_left[0], top_left[1] + Scale / 3 * 2)
    right_one_third = (top_left[0] + Scale, top_left[1] + Scale / 3)
    right_two_third = (top_left[0] + Scale, top_left[1] + Scale / 3 * 2)
    center_one_third_y = (top_left[0] + Scale / 2, top_left[1] + Scale / 3)
    center_two_third_y = (top_left[0] + Scale / 2, top_left[1] + Scale / 3 * 2)
    center_one_third_x = (top_left[0] + Scale / 3, top_left[1] + Scale / 2)
    center_two_third_x = (top_left[0] + Scale / 3 * 2, top_left[1] + Scale / 2)

    # Contains tuples that specify what shapes will be drawn within the square, and whether they are rectangular (True) or not (False)
    shapes_dict = {}

    # Full square
    shape_points = []
    shape_points.append(((top_left, (Scale, Scale)), True))
    shapes_dict[0] = shape_points

    # 1/2 triangles, bases at bottom left and top right
    shape_points = []
    shape_points.append(((top_left, bottom_left, bottom_right), False))
    shape_points.append(((top_left, top_right, bottom_right), False))

    shapes_dict[1] = shape_points

    # 1/2 triangle, bases at top left and bottom right
    shape_points = []
    shape_points.append(((top_left, top_right, bottom_left), False))
    shape_points.append(((top_right, bottom_left, bottom_right), False))

    shapes_dict[2] = shape_points

    # 1/2 rectangles, width > height
    shape_points = []
    shape_points.append(((top_left, (Scale, Scale / 2)), True))
    shape_points.append(((left_center, (Scale, Scale / 2)), True))

    shapes_dict[3] = shape_points

    # 1/2 rectangles, width < height
    shape_points = []
    shape_points.append(((top_left, (Scale / 2, Scale)), True))
    shape_points.append(((top_center, (Scale / 2, Scale)), True))

    shapes_dict[4] = shape_points

    # 1/3 triangles, 'teeth' down
    shape_points = []
    shape_points.append(((top_left, bottom_left, top_center), False))
    shape_points.append(((top_right, bottom_right, top_center), False))
    shape_points.append(((bottom_left, bottom_right, top_center), False))

    shapes_dict[5] = shape_points

    # 1/3 triangles, 'teeth' up
    shape_points = []
    shape_points.append(((top_left, bottom_left, bottom_center), False))
    shape_points.append(((top_right, bottom_right, bottom_center), False))
    shape_points.append(((top_left, top_right, bottom_center), False))

    shapes_dict[6] = shape_points

    # 1/3 triangles, 'teeth' left to right
    shape_points = []
    shape_points.append(((top_left, top_right, left_center), False))
    shape_points.append(((bottom_left, bottom_right, left_center), False))
    shape_points.append(((top_right, bottom_right, left_center), False))

    shapes_dict[7] = shape_points

    # 1/3 triangles, 'teeth' right to left
    shape_points = []
    shape_points.append(((top_left, top_right, right_center), False))
    shape_points.append(((bottom_left, bottom_right, right_center), False))
    shape_points.append(((top_left, bottom_left, right_center), False))

    shapes_dict[8] = shape_points

    # 1/4 triangles, meet in the middle
    shape_points = []
    shape_points.append(((top_left, top_right, center), False))
    shape_points.append(((top_right, bottom_right, center), False))
    shape_points.append(((bottom_left, bottom_right, center), False))
    shape_points.append(((top_left, bottom_left, center), False))

    shapes_dict[9] = shape_points

    # 1/3 rectangles, equal sizes, width > height
    shape_points = []
    shape_points.append(((top_left, (Scale, Scale / 3)), True))
    shape_points.append(((left_one_third, (Scale, Scale / 3)), True))
    shape_points.append(((left_two_third, (Scale, Scale / 3)), True))

    shapes_dict[10] = shape_points

    # 1/3 rectangles, equal sizes, width < height
    shape_points = []
    shape_points.append(((top_left, (Scale / 3, Scale)), True))
    shape_points.append(((top_one_third, (Scale / 3, Scale)), True))
    shape_points.append(((top_two_third, (Scale / 3, Scale)), True))

    shapes_dict[11] = shape_points

    # 1/2 square at top, 1/4 squares at bottom
    shape_points = []
    shape_points.append(((top_left, (Scale, Scale / 2)), True))
    shape_points.append(((left_center, (Scale / 2, Scale / 2)), True))
    shape_points.append(((center, (Scale / 2, Scale / 2)), True))

    shapes_dict[12] = shape_points

    # 1/2 square at bottom, 1/4 squares at top
    shape_points = []
    shape_points.append(((left_center, (Scale, Scale / 2)), True))
    shape_points.append(((top_left, (Scale / 2, Scale / 2)), True))
    shape_points.append(((top_center, (Scale / 2, Scale / 2)), True))

    shapes_dict[13] = shape_points

    # 1/2 square at left, 1/4 squares at right
    shape_points = []
    shape_points.append(((top_left, (Scale / 2, Scale)), True))
    shape_points.append(((top_center, (Scale / 2, Scale / 2)), True))
    shape_points.append(((center, (Scale / 2, Scale / 2)), True))

    shapes_dict[14] = shape_points

    # 1/2 square at right, 1/4 squares at left
    shape_points = []
    shape_points.append(((top_center, (Scale / 2, Scale)), True))
    shape_points.append(((top_left, (Scale / 2, Scale / 2)), True))
    shape_points.append(((left_center, (Scale / 2, Scale / 2)), True))

    shapes_dict[15] = shape_points

    # 1/3 rectangle at top, 2 rectangles at bottom
    shape_points = []
    shape_points.append(((top_left, (Scale, Scale / 3)), True))
    shape_points.append(((left_one_third, (Scale / 2, Scale * 2 / 3)), True))
    shape_points.append(((center_one_third_y, (Scale / 2, Scale * 2 / 3)), True))

    shapes_dict[16] = shape_points

    # 1/3 rectangle at bottom, 2 rectangles at top
    shape_points = []
    shape_points.append(((left_two_third, (Scale, Scale / 3)), True))
    shape_points.append(((top_left, (Scale / 2, Scale * 2 / 3)), True))
    shape_points.append(((top_center, (Scale / 2, Scale * 2 / 3)), True))

    shapes_dict[17] = shape_points

    # 1/3 rectangle at left, 2 rectangles at right
    shape_points = []
    shape_points.append(((top_left, (Scale / 3, Scale)), True))
    shape_points.append(((top_one_third, (Scale * 2 / 3, Scale / 2)), True))
    shape_points.append(((center_one_third_x, (Scale * 2 / 3, Scale / 2)), True))

    shapes_dict[18] = shape_points

    # 1/3 rectangle at right, 2 rectangles at left
    shape_points = []
    shape_points.append(((top_two_third, (Scale / 3, Scale)), True))
    shape_points.append(((top_left, (Scale * 2 / 3, Scale / 2)), True))
    shape_points.append(((left_center, (Scale * 2 / 3, Scale / 2)), True))

    shapes_dict[19] = shape_points

    return shapes_dict
