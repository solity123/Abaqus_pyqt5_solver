# latex: f(x) = \sum_{i=1}^n x_i^2
def sphere(x):
    return sum([xi ** 2 for xi in x])

# latex: f(x) = 10n + \sum_{i=1}^n [x_i^2 - 10 \cos(2\pi x_i)]
def rastrigin(x):
    import math
    return 10 * len(x) + sum([xi ** 2 - 10 * math.cos(2 * math.pi * xi) for xi in x])

# latex: f(x) = \sum_{i=1}^{n-1} [80(x_{i+1} - x_i^2)^2 + (x_i - 1)^2]
def rosenbrock(x):
    return sum([80 * (x[i + 1] - x[i] ** 2) ** 2 + (x[i] - 1) ** 2 for i in range(len(x) - 1)])

# latex: f(x) = \sum_{i=1}^n x_i^4
def sphere_1(x):
    return sum([xi ** 4 for xi in x])

