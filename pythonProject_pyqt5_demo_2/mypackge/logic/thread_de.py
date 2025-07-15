# from PyQt5.QtCore import QThread, pyqtSignal
#
#
# class DEThread(QThread):
#     progress = pyqtSignal(dict)
#     finished = pyqtSignal(dict)
#
#     def __init__(self, parameters):
#         super().__init__()
#         self.params = parameters
#         self._is_running = True
#
#     def run(self):
#         from mypackge.logic.de import DE
#         try:
#             de_generator = DE(self.params, self.progress_report, self.should_stop)
#
#             final_result = None
#             for result in de_generator:
#                 if result.get("final", False):
#                     final_result = result
#                 else:
#                     self.progress.emit(result)
#
#                 if self.should_stop():
#                     self.finished.emit({"status": "stopped"})
#                     return
#
#             if final_result:
#                 self.finished.emit({
#                     "status": "ok",
#                     "best_solution": final_result["best_solution"],
#                     "best_fitness": final_result["best_fitness"]
#                 })
#             else:
#                 self.finished.emit({"status": "error", "message": "未获取最终结果"})
#
#         except Exception as e:
#             self.finished.emit({"status": "error", "message": str(e)})
#
#     def stop(self):
#         self._is_running = False
#
#     def should_stop(self):
#         return not self._is_running
#
#     def progress_report(self, generation, best_fitness, avg_fitness):
#         self.progress.emit({
#             "generation": generation,
#             "best_fitness": best_fitness,
#             "avg_fitness": avg_fitness
#         })

# 未添加目标函数修改的线程
# from PyQt5.QtCore import QThread, pyqtSignal
#
#
# class DEThread(QThread):
#     progress = pyqtSignal(dict)
#     finished = pyqtSignal(dict)
#
#     def __init__(self, parameters):
#         super().__init__()
#         self.params = parameters
#         self._is_running = True
#
#     def run(self):
#         from mypackge.logic.DE import DE  # 根据目录结构调整
#         try:
#             result = DE(
#                 self.params,
#                 callback=self.report_progress,
#                 should_stop=self.should_stop
#             )
#             self.finished.emit(result)
#         except Exception as e:
#             self.finished.emit({"status": "error", "message": str(e)})
#
#     def stop(self):
#         self._is_running = False
#
#     def should_stop(self):
#         return not self._is_running
#
#     def report_progress(self, generation, best_fitness, avg_fitness):
#         self.progress.emit({
#             "generation": generation,
#             "best_fitness": best_fitness,
#             "avg_fitness": avg_fitness
#         })


from PyQt5.QtCore import QThread, pyqtSignal
from sympy import symbols, sympify, lambdify
import numpy as np
from mypackge.logic.DE import DE  # 假设你的 DE 实现在这里

import importlib.util
import os

from PyQt5.QtCore import QMutex, QMutexLocker


def load_functions_from_path(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "objective"):
        raise ValueError("目标函数文件中未定义 `objective(x)` 函数")
    if not callable(module.objective):
        raise ValueError("`objective` 不是函数")
    # return module.objective
    # constraint 可选
    constraint_fn = None
    if hasattr(module, "constraint") and callable(module.constraint):
        constraint_fn = module.constraint

    return module.objective, constraint_fn


class DEThread(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)

    def __init__(self, params, func_expr=None, custom_func_path=None):
        super().__init__()
        self.params = params
        self.func_expr = func_expr
        self._running = True
        self.custom_func_path = custom_func_path
        self.constraint_fn = None

    def stop(self):
        self._running = False

    from sympy import symbols, sympify, lambdify

    # def run(self):
    #     try:
    #         if self.custom_func_path:
    #             objective = load_objective_function_from_path(self.custom_func_path)
    #
    #         # expr = sympify(self.func_expr)
    #         # vars_used = sorted(expr.free_symbols, key=lambda s: s.name)
    #         # f = lambdify(vars_used, expr, modules=["numpy"])
    #         else:
    #             expr = sympify(self.func_expr)
    #             vars_used = sorted(expr.free_symbols, key=lambda s: s.name)
    #             if len(vars_used) != len(self.params["bounds"]):
    #                 raise ValueError("表达式维度与边界不一致")
    #             f = lambdify(vars_used, expr, modules=["numpy"])
    #             objective = (lambda x: f(*x))
    #
    #         # def objective(x):
    #         #     if not self._running:
    #         #         raise Exception("stopped")
    #         #     return f(*x)
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
    #             objective_fn=objective
    #         )
    #         self.finished.emit(result)
    #
    #     except Exception as e:
    #         self.finished.emit({
    #             "status": "error",
    #             "message": str(e)
    #         })

    def run(self):
        try:
            if self.custom_func_path:
                # objective = load_objective_function_from_path(self.custom_func_path)
                objective, constraint = load_functions_from_path(self.custom_func_path)
                self.constraint_fn = constraint
            else:
                expr = sympify(self.func_expr)
                vars_used = sorted(expr.free_symbols, key=lambda s: s.name)
                if len(vars_used) != len(self.params["bounds"]):
                    raise ValueError("函数变量维度与边界维度不一致")
                f = lambdify(vars_used, expr, modules=["numpy"])
                objective = lambda x: f(*x)
                constraint = None

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




#
# class DEThread(QThread):
#     progress = pyqtSignal(dict)
#     finished = pyqtSignal(dict)
#
#     def __init__(self, params, func_expr=None, custom_func_path=None):
#         super().__init__()
#         self.params = params
#         self.mutex = QMutex()
#         self._current_objective = None
#         self._running = True
#         self.update_objective(func_expr, custom_func_path)
#
#     def update_objective(self, func_expr=None, custom_func_path=None):
#         with QMutexLocker(self.mutex):
#             try:
#                 if custom_func_path:
#                     self._current_objective = self._load_custom_function(custom_func_path)
#                 elif func_expr:
#                     self._current_objective = self._parse_expression(func_expr)
#             except Exception as e:
#                 self.finished.emit({"status": "error", "message": f"函数解析失败: {str(e)}"})
#
#     def _load_custom_function(self, path):
#         """线程安全地加载自定义函数文件"""
#         if not os.path.exists(path):
#             raise FileNotFoundError(f"文件不存在: {path}")
#
#         module_name = os.path.splitext(os.path.basename(path))[0]
#         spec = importlib.util.spec_from_file_location(module_name, path)
#         module = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(module)
#
#         if not hasattr(module, "objective"):
#             raise ValueError("目标函数文件中必须定义 objective(x) 函数")
#
#         return module.objective
#
#     def _parse_expression(self, expr_str):
#         """线程安全地解析数学表达式"""
#         expr = sympify(expr_str)
#         vars_used = sorted(expr.free_symbols, key=lambda s: s.name)
#
#         if len(vars_used) != len(self.params["bounds"]):
#             raise ValueError(f"表达式需要 {len(self.params['bounds'])} 个变量")
#
#         f = lambdify(vars_used, expr, modules=["numpy"])
#         return lambda x: f(*x)
#
#     def stop(self):
#         self._running = False
#
#     def run(self):
#         try:
#             while self._running:
#                 # 获取当前目标函数(线程安全)
#                 with QMutexLocker(self.mutex):
#                     objective = self._current_objective
#                     if objective is None:
#                         continue
#
#                 # 运行优化算法
#                 result = self._run_de(objective)
#                 if result is not None:
#                     self.finished.emit(result)
#                     return
#
#         except Exception as e:
#             self.finished.emit({"status": "error", "message": str(e)})
#
#     def _run_de(self, objective):
#         """执行实际的差分进化算法"""
#
#         def callback(gen, best_fit, avg_fit):
#             if not self._running:
#                 raise RuntimeError("用户停止")
#
#             self.progress.emit({
#                 "generation": gen,
#                 "best_fitness": best_fit,
#                 "avg_fitness": avg_fit
#             })
#
#         return DE(
#             params=self.params,
#             callback=callback,
#             should_stop=lambda: not self._running,
#             objective_fn=objective
#         )
