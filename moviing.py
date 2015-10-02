__author__ = 'malbert'
import numpy as np
n = np

def rotMat3D(axis, angle, tol=1e-12):
    """Return the rotation matrix for 3D rotation by angle `angle` degrees about an
    arbitrary axis `axis`.
    """
    t = np.radians(angle)
    x, y, z = axis
    R = (np.cos(t))*np.eye(3) +\
    (1-np.cos(t))*np.matrix(((x**2,x*y,x*z),(x*y,y**2,y*z),(z*x,z*y,z**2))) + \
    np.sin(t)*np.matrix(((0,-z,y),(z,0,-x),(-y,x,0)))
    R[np.abs(R)<tol]=0.0
    return R