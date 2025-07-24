from random import random
from random import sample
from random import uniform
import matplotlib.pyplot as plt
import numpy as np


def performObjective(x):
    total = 0
    for i in range(len(x)):
        total += x[i] ** 2
    return total


def ensureBounds(vec, bounds):
    vec_new = []

    for i in range(len(vec)):

        if vec[i] < bounds[i][0]:
            vec_new.append(bounds[i][0])
        if vec[i] > bounds[i][1]:
            vec_new.append(bounds[i][1])
        if bounds[i][0] <= vec[i] <= bounds[i][1]:
            vec_new.append(vec[i])

    return vec_new


def initialization(algorithmParameters):
    pop_size = algorithmParameters["popSize"]
    bounds = algorithmParameters["bounds"]
    population = []
    for i in range(0, pop_size):
        indv = []
        for j in range(len(bounds)):
            indv.append(uniform(bounds[j][0], bounds[j][1]))
        population.append(indv)

    return population


def DE(params, callback=None, should_stop=lambda: False, objective_fn=None, constraint_fn=None):
    # if objective_fn is None:
    #     raise ValueError("必须提供目标函数 objective_fn")

    bounds = params["bounds"]
    pop_size = params["popSize"]
    mutate = params["mutate rate"]
    cross_rate = params["cross rate"]
    max_iter = params["maximum iterations"]
    dim = len(bounds)

    pop = [np.array([np.random.uniform(low, high) for (low, high) in bounds]) for _ in range(pop_size)]
    fitness = [objective_fn(ind) for ind in pop]
    best_idx = np.argmin(fitness)
    best_ind = pop[best_idx]
    best_fit = fitness[best_idx]

    for gen in range(max_iter):
        if should_stop():
            return {"status": "stopped"}

        new_pop = []
        for i in range(pop_size):
            indices = list(range(0, i)) + list(range(i + 1, pop_size))
            idxs = np.random.choice(indices, 3, replace=False)
            a, b, c = pop[idxs[0]], pop[idxs[1]], pop[idxs[2]]
            mutant = np.clip(a + mutate * (b - c), [b[0] for b in bounds], [b[1] for b in bounds])

            cross_points = np.random.rand(dim) < cross_rate
            if not np.any(cross_points):
                cross_points[np.random.randint(0, dim)] = True

            trial = np.where(cross_points, mutant, pop[i])
            # f = objective_fn(trial) # 更新为下式

            # ✅ 检查约束
            if constraint_fn and not constraint_fn(trial):
                f = float("inf")  # 惩罚非法解
            else:
                f = objective_fn(trial)

            if f < fitness[i]:
                new_pop.append(trial)
                fitness[i] = f
                if f < best_fit:
                    best_ind = trial
                    best_fit = f
            else:
                new_pop.append(pop[i])
        pop = new_pop

        if callback:
            callback(gen, best_fit, np.mean(fitness))

    return {
        "status": "ok",
        "best_solution": best_ind.tolist(),
        "best_fitness": best_fit
    }


if __name__ == "__main__":
    #
    # algorithmParameters = {"bounds": [(-1, 1), (-1, 1)],
    #                        "popSize": 10,
    #                        "mutate rate": 0.5,
    #                        "cross rate": 0.8,
    #                        "maximum iterations": 20}
    # DE(algorithmParameters)
    pass
