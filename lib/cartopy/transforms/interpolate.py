import numpy as np


def haversin(x):
    return np.sin(x / 2) ** 2


def great_circle_interpolation(p0, p1):
    # A quick and dirty implementation of spherical interpolation.
    # Needs doing properly.

    x0, y0 = np.deg2rad(p0)
    x1, y1 = np.deg2rad(p1)

    cy0 = np.cos(y0)
    sy0 = np.sin(y0)
    cy1 = np.cos(y1)
    sy1 = np.sin(y1)
    kx0 = cy0 * np.cos(x0)
    ky0 = cy0 * np.sin(x0)
    kx1 = cy1 * np.cos(x1)
    ky1 = cy1 * np.sin(x1)
    d = 2 * np.arcsin(np.sqrt(haversin(y1 - y0) + cy0 * cy1 * haversin(x1 - x0)))
    k = 1. / np.sin(d)

    def interpolator(t):
        # XXX B was (t *= d) - what is that?
        B = np.sin(t * d) * k
        A = np.sin(d - (t * d)) * k
        x = A * kx0 + B * kx1
        y = A * ky0 + B * ky1
        z = A * sy0 + B * sy1

        # Return z?
        return np.rad2deg([np.arctan2(y, x),
                           np.arctan2(z, np.sqrt(x * x + y * y))])
    return interpolator


if __name__ == '__main__':
    interpolator = great_circle_interpolation([-40, 40], [100, 60])

    import matplotlib.pyplot as plt

    x, y = np.array([interpolator(t) for t in np.linspace(-0.5, 1, 10)]).T
    print x
    print y
    plt.plot(x, y)
    print interpolator(0.5)
    plt.show()
