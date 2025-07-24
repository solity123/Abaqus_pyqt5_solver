from PyQt5.QtCore import pyqtSignal, QObject
from mypackge.logic.DE_algorithm.thread_de import DEThread


class DEController(QObject):
    """封装DE算法线程控制逻辑"""
    progress_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.de_thread = None

    def run(self, params, objective_function=None, constraint_function=None):
        """启动 DE 算法线程"""
        """注意此处 仅可单独运算 要并行运算时 应修改"""
        if self.de_thread and self.de_thread.isRunning():
            self.progress_signal.emit({
                "generation": -1,
                "best_fitness": None,
                "avg_fitness": None,
                "message": "⚠️ 差分进化正在运行，请先停止"
            })
            return

        # ✅ 设置默认目标函数（防止 None）
        if objective_function is None:
            def default_objective_func(x):
                return x[0] ** 2 + x[1] ** 2

            objective_function = default_objective_func

        # ✅ 设置默认约束函数（防止 None）
        if constraint_function is None:
            def default_constraint_func(x):
                return x[0] ** 2 + x[1] ** 2

            constraint_function = default_constraint_func

        self.de_thread = DEThread(
            params=params,
            objective_function=objective_function,
            constraint_function=constraint_function,
        )

        self.de_thread.progress.connect(self.progress_signal.emit)
        self.de_thread.finished.connect(self._handle_finished)

        self.de_thread.start()

    def stop(self):
        """请求中止 DE 线程"""
        if self.de_thread and self.de_thread.isRunning():
            self.de_thread.stop()
            self.progress_signal.emit({
                "generation": -1,
                "message": "🛑 用户请求停止差分进化"
            })

    def _handle_finished(self, result):
        if isinstance(result, dict):
            if "status" in result and result["status"] == "ok":
                try:
                    self.progress_signal.emit({
                        "generation": -1,
                        "message": f"✅ 差分进化完成，最优值：{result['best_fitness']:.4f}"
                    })
                except Exception as e:
                    print("⚠️ 信号发射异常：", e)
            elif result.get("status") == "stopped":
                try:
                    self.progress_signal.emit({
                        "generation": -1,
                        "message": "🛑 差分进化被用户中止"
                    })
                except Exception as e:
                    print("⚠️ 信号发射异常：", e)
            else:
                try:
                    self.progress_signal.emit({
                        "generation": -1,
                        "message": f"❌ 异常：{result.get('message', '未知错误')}"
                    })
                except Exception as e:
                    print("⚠️ 信号发射异常：", e)
        else:
            try:
                self.progress_signal.emit({
                    "generation": -1,
                    "message": "❌ 未知错误：返回结果无效"
                })
            except Exception as e:
                print("⚠️ 信号发射异常：", e)
        try:
            self.finished_signal.emit(result)
        except Exception as e:
            print("⚠️ 信号发射异常：", e)
    # def _handle_finished(self, result):
    #     self.finished_signal.emit(result)
