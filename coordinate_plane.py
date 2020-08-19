class Point:
    def __init__(self, x, y):
        """
        A 2D coordinate Point object consisting of an x value and a y value.
        :param x: Float representing the x-coordinate of the point object
        :param y: Float representing the y-coordinate of the point object
        """
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)


def on_segment(p, q, r):
    """
    Returns True if q is a point on segment pr. Otherwise, False
    :param p: Point object of first end of segment
    :param q: Point object checking if it is on segment pr.
    :param r: Point object of second end of segment
    :return: Boolean
    """
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    """
    Returns an integer depending on the orientation of three Point objects.
    :param p: Point object
    :param q: Point object
    :param r: Point object
    :return: Int - returns 1 if clockwise, 2 if counter clockwise, or 0 if colinear.
    """
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Colinear orientation
        return 0


def do_intersect(p1, q1, p2, q2):
    """
    Checks if segment p1 to q1 intersects p2 to q2.
    :param p1: Point object
    :param q1: Point object
    :param p2: Point object
    :param q2: Point object
    :return: Boolean - True if p1q1 intersects p2q1. Otherwise, False.
    """
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0) and on_segment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if (o2 == 0) and on_segment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0) and on_segment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0) and on_segment(p2, q1, q2):
        return True

    # If none of the cases
    return False


def do_intersect_exclude_on_segment(corners, p1, q1):
    """
    Checks if the segment p1 to q1 is intersected by any of the walls made up of the corners. However, unlike
    do_intersect, the function does not return True if a corner point likes on the segment p1 q1.
    :param corners: list of coordinates which correspond to corners of an object or closed shape
    :param p1: Point object representing the first end of the segment
    :param q1: Point object representing the second end of the segment
    :return: Boolean - True if corners do intersect segment p1 to q1. Otherwise, False.
    """
    for i in range(len(corners)):
        (x3, y3), (x4, y4) = corners[i], corners[(i + 1) % len(corners)]
        p2 = Point(x3, y3)
        q2 = Point(x4, y4)
        if on_segment(p2, q1, q2):
            continue
        if do_intersect(p1, q1, p2, q2):
            return True
    return False


def find_line_equation(p1, p2):
    """
    Returns the 2D coordinate plane line equation of the segment p1 to p2. The equation is returned in the form of
    3 different fields.
    :param p1: Point object representing the first end of the segment
    :param p2: Point object representing the second end of the segment
    :return: String - "y" if the line is not vertical. Otherwise "x".
             [m] - slope of the line. If the line is horizontal or vertical, it is the corresponding y or x value.
             [b] - intercept of the line. If the line is horizontal or vertical, it has no intercept and returns None.
    """
    delta_x = p2.x - p1.x
    delta_y = p2.y - p1.y
    if delta_y ** 2 < 0.0001:
        return "y", p1.y, None
    elif delta_x ** 2 < 0.0001:
        return "x", p1.x, None
    else:
        m = delta_y / delta_x
        b = p2.y - (m * p2.x)
        return "y", m, b


def find_intersection(p1, p2, q1, q2):
    """
    Returns the intersection point of two segments if they were to be extended.
    :param p1: Point object representing the first end of the segment p
    :param p2: Point object representing the second end of the segment p
    :param q1: Point object representing the first end of the segment q
    :param q2: Point object representing the second end of the segment q
    :return: Point - Point object representing the intersection point between segment p and segment q extended.
    """
    p_axis, p_val, p_inter = find_line_equation(p1, p2)
    q_axis, q_val, q_inter = find_line_equation(q1, q2)
    if p_inter is None and q_inter is None:
        if p_axis == q_axis:
            return None
        elif p_axis == "x":
            return Point(p_val, q_val)
        else:
            return Point(q_val, p_val)
    elif p_inter is None:
        if p_axis == "y":
            x = (p_val - q_inter) / q_val
            return Point(x, p_val)
        else:
            y = (q_val * p_val) + q_inter
            return Point(p_val, y)
    elif q_inter is None:
        if q_axis == "y":
            x = (q_val - p_inter) / p_val
            return Point(x, q_val)
        else:
            y = (p_val * q_val) + p_inter
            return Point(q_val, y)
    else:
        delta_b = p_inter - q_inter
        delta_m = q_val - p_val
        x = delta_b / delta_m
        y = (q_val * x) + q_inter
        return Point(x, y)
