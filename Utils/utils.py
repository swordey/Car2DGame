import numpy as np
# intersection functions are originated from here
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/

# intersection distance originates from here
# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect

def calcIntersectionPoint2(line1,line2):
    A = line1[0:2]
    B = line1[2:4]
    C = line2[0:2]
    D = line2[2:4]

    nom1 = (D[0]-C[0])*(A[1]-C[1])-(D[1]-C[1])*(A[0]-C[0])
    nom2 = (B[0]-A[0])*(A[1]-C[1])-(B[1]-A[1])*(A[0]-C[0])
    den = (D[1]-C[1])*(B[0]-A[0])-(D[0]-C[0])*(B[1]-A[1])

    if nom1 != 0 and nom2 != 0 and den != 0:
        ua = nom1/den
        ub = nom2/den
        if 0<=ua<=1 and 0<=ub<=1:
            new_point = np.array([C[0]+ub*(D[0]-C[0]),C[1]+ub*(D[1]-C[1])]).astype(int)
            return np.sqrt(ub*(D[0]-C[0])**2+ub*(D[1]-C[1])**2), new_point
        else:
            return None, None
    else:
        return None,None

def calcIntersectionPoint(line1,line2):
    A = line1[0:2]
    B = line1[2:4]
    C = line2[0:2]
    D = line2[2:4]
    E = B - A
    F = D - C
    P = np.array([-E[1],E[0]])

    denom = np.array(F*P).astype(int)
    if denom[0] == 0 or denom[1] == 0:
        return None, None
    else:
        h = ((A - C) * P)/(denom)
        if 0<= h[0] <= 1 and 0<= h[1] <= 1:
            return sum(h**2), np.array(C + F*h).astype(int)
        else:
            return None, None

def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


def orientation(p, q, r):
    '''
    To find orientation of ordered triplet (p, q, r).
    :param p: 2d point
    :param q: 2d point
    :param r: 2d point
    :return:
        0 --> p, q and r are colinear
        1 --> Clockwise
        2 --> Counterclockwise
    '''
    val = (q[1]-p[1])*(r[0]-q[0]) \
          - (q[0]-p[0])*(r[1]-q[1])

    if val == 0:
        return 0

    return 1 if (val>0) else 2


def onSegment(p,q,r):
    if max(p[0],r[0]) >= q[0] >= min(p[0],r[0]) \
            and max(p[0],r[1]) >= q[0] >= min(p[0],r[1]):
        return True
    return False


def doIntersect(p1,q1,p2,q2):
    '''
    The main function that returns true if line segment 'p1q1'
    and 'p2q2' intersect.
    :param p1: 2d point
    :param q1: 2d point
    :param p2: 2d point
    :param q2: 2d point
    :return:
        True - two line intersects
        False - two line doesn't intersect
    '''
    o1 = orientation(p1,q1,p2)
    o2 = orientation(p1,q1,q2)
    o3 = orientation(p2,q2,p1)
    o4 = orientation(p2,q2,q1)

    # General case
    if o1 != o2 and o3 != o4:
        return True
    # Special cases
    # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if o1==0 and onSegment(p1,p2,q1): return True
    # p1, q1 and q2 are colinear and q2 lies on segment p1q1
    if o2 == 0 and onSegment(p1, q2, q1): return True
    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if o3 == 0 and onSegment(p2, p1, q2): return True
    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if o4 == 0 and onSegment(p2, q1, q2): return True

    return False