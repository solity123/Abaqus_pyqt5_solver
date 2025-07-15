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


# def DE(algorithmParameters):
#     maxIter = algorithmParameters["maximum iterations"]
#     pop_size = algorithmParameters["popSize"]
#     mutate_rate = algorithmParameters["mutate rate"]
#     cross_rate = algorithmParameters["cross rate"]
#     bounds = algorithmParameters["bounds"]
#
#     population = initialization(algorithmParameters)
#
#     gen_avg_record = []
#     gen_best_record = []
#
#     for i in range(1, maxIter + 1):
#         print("Generation :", i)
#
#         gen_scores = []
#
#         for j in range(0, pop_size):
#
#             candidate = list(range(0, pop_size))
#             candidate.remove(j)
#             random_index = sample(candidate, 3)
#
#             x_1 = population[random_index[0]]
#             x_2 = population[random_index[1]]
#             x_3 = population[random_index[2]]
#
#             x_t = population[j]
#
#             #
#             x_diff = [x_2_i - x_3_i for x_2_i, x_3_i in zip(x_2, x_3)]
#
#             # mutation
#             v_donor = [x_1_i + mutate_rate * x_diff_i for x_1_i, x_diff_i in zip(x_1, x_diff)]
#
#             v_donor_new = []
#
#             for p in range(len(v_donor)):
#
#                 if v_donor[p] < bounds[p][0]:
#                     v_donor_new.append(bounds[p][0])
#                 if v_donor[p] > bounds[p][1]:
#                     v_donor_new.append(bounds[p][1])
#                 if bounds[p][0] <= v_donor[p] <= bounds[p][1]:
#                     v_donor_new.append(v_donor[p])
#
#             v_donor = v_donor_new
#
#             ## Cross
#             v_trial = []
#             for k in range(len(x_t)):
#                 crossover = random()
#
#                 if crossover <= cross_rate:
#                     v_trial.append(v_donor[k])
#                 else:
#                     v_trial.append(x_t[k])
#
#             ## Greedy selection
#             score_trial = 0
#             for i in range(len(v_trial)):
#                 score_trial += v_trial[i] ** 2
#
#             score_target = 0
#             for i in range(len(x_t)):
#                 score_target += x_t[i] ** 2
#
#             if score_trial < score_target:
#                 population[j] = v_trial
#                 gen_scores.append(score_trial)
#                 print('     >>', score_trial, v_trial)
#
#             else:
#                 gen_scores.append(score_target)
#                 print('     >>', score_target, x_t)
#
#         gen_avg = sum(gen_scores) / pop_size
#         gen_best = min(gen_scores)
#         gen_avg_record.append(gen_avg)
#         gen_best_record.append(gen_best)
#
#         gen_sol = population[gen_scores.index(min(gen_scores))]
#
#         print("        >> Generation Average: ", gen_avg)
#         print("        >> Generation Bset: ", gen_best)
#         print("        >> Best solution: ", gen_sol, '\n')
#
#     plt.plot([i for i in range(len(gen_best_record))], gen_best_record, 'b')
#     plt.plot([i for i in range(len(gen_avg_record))], gen_avg_record, 'r')
#     plt.ylabel('fitness', fontsize=15)
#     plt.xlabel('generation', fontsize=15)
#     plt.xticks([0, 5, 10, 15, 20])
#     plt.legend(["gen_best", "gen_avg"])
#     plt.show()
#     return {
#         "best_solution": gen_sol,
#         "best_fitness": gen_best,
#         "avg_fitness": gen_avg,
#         "generation_records": {
#             "best": gen_best_record,
#             "avg": gen_avg_record
#         }
#     }
#     # for i in range(1, maxIter + 1):
#     #     ...
#     #     # yield 每代的状态信息
#     #     yield {
#     #         "generation": i,
#     #         "best_fitness": gen_best,
#     #         "avg_fitness": gen_avg,
#     #         "best_solution": gen_sol
#     #     }
#     #
#     #     # 最后也 yield 一个收尾结果（可选）
#     # yield {
#     #     "generation": maxIter,
#     #     "best_fitness": gen_best,
#     #     "avg_fitness": gen_avg,
#     #     "best_solution": gen_sol,
#     #     "final": True
#     # }

# 未自定义function的de算法
# def DE(params, callback=None, should_stop=lambda: False):
#     bounds = params["bounds"]
#     pop_size = params["popSize"]
#     mutate = params["mutate rate"]
#     cross_rate = params["cross rate"]
#     max_iter = params["maximum iterations"]
#
#     dim = len(bounds)
#     pop = [np.array([np.random.uniform(low, high) for (low, high) in bounds]) for _ in range(pop_size)]
#
#     fitness = [performObjective(ind) for ind in pop]
#     best_idx = np.argmin(fitness)
#     best_ind = pop[best_idx]
#     best_fit = fitness[best_idx]
#
#     for gen in range(max_iter):
#         if should_stop():
#             return {"status": "stopped"}
#
#         new_pop = []
#         # for i in range(pop_size):
#         #     indices = list(range(0, i)) + list(range(i + 1, pop_size))
#         #     a, b, c = pop[np.random.choice(indices, 3, replace=False)]
#         #     mutant = np.clip(a + mutate * (b - c), [b[0] for b in bounds], [b[1] for b in bounds])
#         #     cross_points = np.random.rand(dim) < cross_rate
#         #     if not np.any(cross_points):
#         #         cross_points[np.random.randint(0, dim)] = True
#         #     trial = np.where(cross_points, mutant, pop[i])
#         for i in range(pop_size):
#             indices = list(range(0, i)) + list(range(i + 1, pop_size))
#             idxs = np.random.choice(indices, 3, replace=False)
#             a, b, c = pop[idxs[0]], pop[idxs[1]], pop[idxs[2]]
#
#             mutant = np.clip(a + mutate * (b - c), [b[0] for b in bounds], [b[1] for b in bounds])
#
#             cross_points = np.random.rand(dim) < cross_rate
#             if not np.any(cross_points):
#                 cross_points[np.random.randint(0, dim)] = True
#
#             trial = np.where(cross_points, mutant, pop[i])
#
#             f = performObjective(trial)
#             if f < fitness[i]:
#                 new_pop.append(trial)
#                 fitness[i] = f
#                 if f < best_fit:
#                     best_ind = trial
#                     best_fit = f
#             else:
#                 new_pop.append(pop[i])
#
#         pop = new_pop
#
#         if callback:
#             avg_fit = np.mean(fitness)
#             callback(gen, best_fit, avg_fit)
#
#     return {
#         "status": "ok",
#         "best_solution": best_ind.tolist(),
#         "best_fitness": best_fit
#     }
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
