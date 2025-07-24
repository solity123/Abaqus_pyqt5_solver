from mypackge.logic.DE_algorithm.DE import DE
import numpy as np
def run_de_algorithm(params, objective_fn, constraint_fn=None):
    def callback(gen, best, mean):
        print(f"🌀 第 {gen+1} 代 | 最优值: {best:.4f} | 平均适应度: {mean:.4f}")

    result = DE(params, callback=callback, objective_fn=objective_fn, constraint_fn=constraint_fn)
    return result

if __name__ == "__main__":
    # 目标函数：f(x) = x1² + x2²
    # def f(x): return x[0]**2 + x[1]**2
    def f(x):
        return sum(xi ** 2 for xi in x)
    # 约束函数（始终满足）
    def g(x): return np.all(x >= 0) and np.sum(x) <= 5

    # 参数设置
    params = {
        "bounds": [(-1, 1), (-1, 1)],
        "popSize": 10,
        "mutate rate": 0.5,
        "cross rate": 0.8,
        "maximum iterations": 20
    }

    # 运行差分进化
    result = run_de_algorithm(params, f, g)
    print("✅ 最终结果:", result)
