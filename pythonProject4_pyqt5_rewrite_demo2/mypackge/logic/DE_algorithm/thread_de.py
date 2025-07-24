# DE algorithm 的线程
from PyQt5.QtCore import QThread, pyqtSignal
from sympy import sympify, lambdify
from mypackge.logic.DE_algorithm.DE import DE  # 假设你的 DE 实现在这里

import importlib.util
import os
import warnings
import numpy as np


def load_functions_from_path(file_path):
    # 预设默认目标函数（返回0的简单函数）
    def default_objective(x):
        return sum(xi ** 2 for xi in x)

    # 预设默认约束函数（返回空列表）
    def default_constraint(x):
        return np.all(x >= 0) and np.sum(x) <= 5

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 初始化目标函数（优先使用模块中的定义）
    objective_fn = default_objective
    if hasattr(module, "objective"):
        if callable(module.objective):
            objective_fn = module.objective
        else:
            warnings.warn("`objective` is not callable, using default", UserWarning)
    else:
        warnings.warn("No `objective` function defined, using default", UserWarning)

    # 初始化约束函数（优先使用模块中的定义）
    constraint_fn = default_constraint
    if hasattr(module, "constraint"):
        if callable(module.constraint):
            constraint_fn = module.constraint
        else:
            warnings.warn("`constraint` is not callable, using default", UserWarning)
    else:
        warnings.warn("No `constraint` function defined, using default", UserWarning)

    return objective_fn, constraint_fn


class DEThread(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)

    def __init__(self, params, objective_function=None, constraint_function=None):
        super().__init__()
        self.params = params
        self.objective_function = objective_function
        self._running = True
        self.constraint_function = constraint_function
        self.constraint_fn = None

    def stop(self):
        self._running = False

    # def run(self):
    #     print("DEThread run() 被调用")
    #     print("传入的objective_function函数表达式：", self.objective_function)
    #     print("传入的constraint_function函数表达式：", self.constraint_function)
    #     print("传入的参数：", self.params)
    #     try:
    #         # if self.constraint_function:
    #         #     objective, constraint = load_functions_from_path(self.constraint_function)
    #         #     self.constraint_fn = constraint
    #         if self.constraint_function is None or objective_function is None:
    #             objective, constraint = objective_function, constraint_function
    #         else:
    #             expr = sympify(self.objective_function)
    #             vars_used = sorted(expr.free_symbols, key=lambda s: s.name)
    #             if len(vars_used) != len(self.params["bounds"]):
    #                 raise ValueError("函数变量维度与边界维度不一致")
    #             f = lambdify(vars_used, expr, modules=["numpy"])
    #             objective = lambda x: f(*x)
    #             constraint = None
    #
    #         def should_stop():
    #             return not self._running
    #
    #         def callback(gen, best_fit, avg_fit):
    #             self.progress.emit({
    #                 "generation": gen,
    #                 "best_fitness": best_fit,
    #                 "avg_fitness": avg_fit
    #             })
    #
    #         result = DE(
    #             params=self.params,
    #             callback=callback,
    #             should_stop=should_stop,
    #             objective_fn=objective,
    #             constraint_fn=constraint
    #         )
    #         self.finished.emit(result)
    #
    #     except Exception as e:
    #         self.finished.emit({
    #             "status": "error",
    #             "message": str(e)
    #         })

    def run(self):
        print("DEThread run() 被调用")
        print("传入的objective_function函数表达式：", self.objective_function)
        print("传入的constraint_function函数表达式：", self.constraint_function)
        print("传入的参数：", self.params)
        try:
            objective = self.objective_function
            constraint = self.constraint_function

            def should_stop():
                return not self._running

            def callback(gen, best_fit, avg_fit):
                self.progress.emit({
                    "generation": gen,
                    "best_fitness": best_fit,
                    "avg_fitness": avg_fit
                })

            result = DE(
                params=self.params,
                callback=callback,
                should_stop=should_stop,
                objective_fn=objective,
                constraint_fn=constraint
            )
            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({
                "status": "error",
                "message": str(e)
            })







