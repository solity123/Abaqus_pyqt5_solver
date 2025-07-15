# 逻辑部分
import sys
import os
from mypackge.ui.MainWindow_refine import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QDialogButtonBox, QFileDialog
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from mypackge.logic.thread_de import DEThread
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib


matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体（SimHei）
matplotlib.rcParams['axes.unicode_minus'] = False    # 正常显示负号


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)  # 使用super()的标准写法

        # 使用组合模式初始化UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 获取显示器分辨率
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()
        print("Screen height {}".format(self.screenheight))
        print("Screen width {}".format(self.screenwidth))
        self.width = int(self.screenwidth * 0.75)
        self.height = int(self.screenheight * 0.83)
        self.resize(self.width, self.height)

        self._init_menu_states()  # 改写meun的初始化
        self.setup_textbrowser_font()  # textbrower的fontsize自适应 （8，width/10）之间
        self._init_parameter_inputs()  # 初始化 参数的lineedit
        self._init_de_controls()  # button star and stop

        self._init_de_plot()  # 调用graphicsView_result_show的matplotlib画图初始化

        # 初始化导入函数的路径
        self.custom_function_path = None

    # 初代 隐藏显示 代码尝试
    # def hide_menu_customize_function(self):
    #     self.ui.action_customize_function.setVisible(not self.ui.verticalLayout_2.isVisible())
    #     self.ui.action_paramater_optimize.setVisible(self.ui.verticalLayout_4.isVisible())
    #
    # def hide_menu_paramater_optimize(self):
    #     self.ui.action_paramater_optimize.setVisible(not self.ui.verticalLayout_2.isVisible())
    #     self.ui.action_customize_function.setVisible(self.ui.verticalLayout_4.isVisible())

    # 隐藏显示代码
    def _init_menu_states(self):
        """初始化菜单显示状态"""
        self._set_layout_visibility(self.ui.verticalLayout_2, True)
        self._set_layout_visibility(self.ui.verticalLayout_4, False)
        self.ui.action_customize_function.setChecked(False)
        self.ui.action_paramater_optimize.setChecked(False)
        self.ui.textBrowser_mode_show.setText("优化参数设置")

    def _set_layout_visibility(self, layout, visible: bool):
        """
        设置一个布局中所有控件的可见性
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setVisible(visible)

    def toggle_menu(self, show_layout, hide_layout, action):
        """
        切换两个布局中控件的可见性
        :param show_layout: 要显示的布局
        :param hide_layout: 要隐藏的布局
        :param action: 被点击的 QAction
        """
        # 获取当前可见状态
        any_visible = any(show_layout.itemAt(i).widget().isVisible() for i in range(show_layout.count()) if
                          show_layout.itemAt(i).widget())

        # 显隐切换
        self._set_layout_visibility(show_layout, not any_visible)
        self._set_layout_visibility(hide_layout, False)

        # 设置菜单选中状态
        action.setChecked(not any_visible)
        if show_layout == self.ui.verticalLayout_2:
            self.ui.action_customize_function.setChecked(False)
        else:
            self.ui.action_paramater_optimize.setChecked(False)

    def textBrower_show(self, action):
        try:
            if action == self.ui.action_paramater_optimize:
                self.ui.textBrowser_mode_show.setText("优化参数设置")
            elif action == self.ui.action_customize_function:
                self.ui.textBrowser_mode_show.setText("自定义函数")
        except Exception as e:
            print(f"切换菜单错: {e}")

    def handle_parameter_optimize(self):
        self.toggle_menu(
            self.ui.verticalLayout_2,
            self.ui.verticalLayout_4,
            self.ui.action_paramater_optimize
        )
        self.textBrower_show(self.ui.action_paramater_optimize)

    def handle_custom_function(self):
        self.toggle_menu(
            self.ui.verticalLayout_4,
            self.ui.verticalLayout_2,
            self.ui.action_customize_function
        )
        self.textBrower_show(self.ui.action_customize_function)

    def setup_textbrowser_font(self):
        # 设置字体为楷体
        font = QFont("楷体")
        self.ui.textBrowser_mode_show.setFont(font)

        # 设置自动换行
        self.ui.textBrowser_mode_show.setWordWrapMode(True)

        # 监听窗口大小变化，动态调整字号
        self.ui.textBrowser_mode_show.resizeEvent = self.adjust_font_size

    def adjust_font_size(self, event):
        # 获取当前控件大小
        width = self.ui.textBrowser_mode_show.width()
        height = self.ui.textBrowser_mode_show.height()

        # 根据控件大小计算合适的字号（示例：按宽度比例调整）
        font_size = max(8, int(width / 10))  # 最小字号8，按比例调整
        font = self.ui.textBrowser_mode_show.font()
        font.setPointSize(font_size)
        self.ui.textBrowser_mode_show.setFont(font)

        # 调用父类 resizeEvent 确保正常渲染
        super(QTextBrowser, self.ui.textBrowser_mode_show).resizeEvent(event)

# DE 算法的调用和参数调整
    def _init_de_controls(self):
        """初始化DE算法控制按钮"""
        # 连接按钮信号
        self.ui.buttonBox_star_stop.accepted.connect(self.start_de_algorithm)
        self.ui.buttonBox_star_stop.rejected.connect(self.stop_de_algorithm)

        # 设置按钮文本
        self.ui.buttonBox_star_stop.button(QDialogButtonBox.Ok).setText("开始")
        self.ui.buttonBox_star_stop.button(QDialogButtonBox.Cancel).setText("停止")

        # 初始状态
        self.de_thread = None
        self.de_running = False

    # def start_de_algorithm(self):
    #     """启动DE算法"""
    #     if self.de_running:
    #         self.ui.textBrowser_result_show.append("DE算法已在运行中...")
    #         return
    #
    #     params = self.get_algorithm_parameters()
    #     if params:
    #         self.ui.textBrowser_result_show.append("正在启动DE算法...")
    #         self.ui.textBrowser_result_show.append(f"参数: {params}")
    #
    #         # 禁用开始按钮
    #         self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
    #
    #         # 在子线程中运行算法
    #         self.de_thread = DEThread(params)
    #         self.de_thread.finished.connect(self.on_de_finished)
    #         self.de_thread.progress.connect(self.on_de_progress)
    #         self.de_thread.start()
    #
    #         self.de_running = True
    # 添加图表前修复的function
    # def start_de_algorithm(self):
    #     if self.de_thread and self.de_thread.isRunning():
    #         self.ui.textBrowser_result_show.append("算法正在运行中...")
    #         return
    #
    #     params = self.get_algorithm_parameters()
    #     if not params:
    #         return
    #
    #     self.ui.textBrowser_result_show.append("开始运行 DE 算法...")
    #     self.de_thread = DEThread(params)
    #     self.de_thread.progress.connect(self.on_de_progress)
    #     self.de_thread.finished.connect(self.on_de_finished)
    #     self.de_thread.start()
    #
    #     self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

# 原未自定义function的启动函数
    # def start_de_algorithm(self):
    #     if self.de_thread and self.de_thread.isRunning():
    #         self.ui.textBrowser_result_show.append("算法正在运行中...")
    #         return
    #
    #     try:
    #         params = self.get_algorithm_parameters()
    #         if not params:
    #             return
    #
    #         self.ui.textBrowser_result_show.append("开始运行 DE 算法...")
    #         self.de_thread = DEThread(params)
    #         self.de_thread.progress.connect(self.on_de_progress)
    #         self.de_thread.finished.connect(self.on_de_finished)
    #         self.de_thread.start()
    #
    #         self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
    #
    #         self.best_fitness_list = []
    #         self.avg_fitness_list = []
    #         self.ax.clear()
    #         self.canvas.draw()
    #
    #     except Exception as e:
    #         self.ui.textBrowser_result_show.append(f"启动算法失败：{e}")
    def start_de_algorithm(self):
        if self.de_thread and self.de_thread.isRunning():
            self.ui.textBrowser_result_show.append("算法正在运行中...")
            return

        try:
            params = self.get_algorithm_parameters()

            if not hasattr(self.ui, "lineEdit_customize_function"):
                self.ui.textBrowser_result_show.append("找不到目标函数输入框")
                return

            func_expr = self.ui.lineEdit_customize_function.text().strip()

            if not params or not func_expr:
                self.ui.textBrowser_result_show.append("请填写完整的参数与函数表达式")
                return

            self.ui.textBrowser_result_show.append("开始运行 DE 算法...")

            # self.de_thread = DEThread(params, func_expr=func_expr)
            self.de_thread = DEThread(params, func_expr=func_expr, custom_func_path=self.custom_function_path)

            self.de_thread.progress.connect(self.on_de_progress)
            self.de_thread.finished.connect(self.on_de_finished)
            self.de_thread.start()

            self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.best_fitness_list = []
            self.avg_fitness_list = []
            self.ax.clear()
            self.canvas.draw()
        except Exception as e:
            self.ui.textBrowser_result_show.append(f"启动算法失败：{e}")

    # def stop_de_algorithm(self):
    #     """停止DE算法"""
    #     if self.de_thread and self.de_running:
    #         self.ui.textBrowser_result_show.append("正在停止DE算法...")
    #         self.de_thread.terminate()  # 强制终止线程
    #         self.de_thread.wait()
    #         self.on_de_finished({"status": "stopped"})
    #     else:
    #         self.ui.textBrowser_mode_result.append("没有正在运行的DE算法")
    def stop_de_algorithm(self):
        if self.de_thread and self.de_thread.isRunning():
            self.ui.textBrowser_result_show.append("正在终止算法...")
            self.de_thread.stop()
        else:
            self.ui.textBrowser_result_show.append("没有正在运行的算法。")

    # def on_de_progress(self, info):
    #     """DE算法进度更新"""
    #     gen = info["generation"]
    #     best = info["best_fitness"]
    #     avg = info["avg_fitness"]
    #
    #     self.ui.textBrowser_result_show.append(
    #         f"Generation {gen}: 最佳适应度={best:.4f}, 平均适应度={avg:.4f}")
    # def on_de_progress(self, info):
    #     gen = info["generation"]
    #     best = info["best_fitness"]
    #     avg = info["avg_fitness"]
    #     self.ui.textBrowser_result_show.append(
    #         f"[第 {gen} 代] 最佳适应度：{best:.4f}，平均适应度：{avg:.4f}")
    def on_de_progress(self, info):
        gen = info["generation"]
        best = info["best_fitness"]
        avg = info["avg_fitness"]

        self.ui.textBrowser_result_show.append(
            f"[第 {gen} 代] 最佳适应度：{best:.4f}，平均适应度：{avg:.4f}"
        )

        self.best_fitness_list.append(best)
        self.avg_fitness_list.append(avg)

        # 更新图表
        self.ax.clear()
        self.ax.plot(self.best_fitness_list, label="Best Fitness", color="blue")
        self.ax.plot(self.avg_fitness_list, label="Avg Fitness", color="green")
        self.ax.set_title("DE 适应度曲线")
        self.ax.set_xlabel("迭代代数")
        self.ax.set_ylabel("适应度")
        self.ax.legend()
        self.canvas.draw()

    # def on_de_finished(self, result):
    #     """DE算法完成后的回调"""
    #     self.de_running = False
    #     self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
    #
    #     if result.get("status") == "stopped":
    #         self.ui.textBrowser_result_show.append("DE算法已停止")
    #     else:
    #         self.ui.textBrowser_result_show.append("DE算法运行完成!")
    #         self.ui.textBrowser_result_show.append(f"最佳解: {result['best_solution']}")
    #         self.ui.textBrowser_result_show.append(f"最佳适应度: {result['best_fitness']:.6f}")
    def on_de_finished(self, result):
        self.ui.buttonBox_star_stop.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

        if result.get("status") == "error":
            self.ui.textBrowser_result_show.append(f"算法出错：{result['message']}")
        elif result.get("status") == "stopped":
            self.ui.textBrowser_result_show.append("算法被手动终止。")
        else:
            self.ui.textBrowser_result_show.append("算法运行完成！")
            self.ui.textBrowser_result_show.append(f"最佳解：{result['best_solution']}")
            self.ui.textBrowser_result_show.append(f"最佳适应度：{result['best_fitness']:.6f}")

    def _init_parameter_inputs(self):
        """初始化DE算法参数输入框"""
        # 设置默认值
        self.ui.lineEdit_bounds.setText("[(-1, 1), (-1, 1)]")
        self.ui.lineEdit_popSize.setText("10")
        self.ui.lineEdit_mutate_rate.setText("0.5")
        self.ui.lineEdit_cross_rate.setText("0.8")
        self.ui.lineEdit_max_iterations.setText("20")
        # 初始化自定义目标函数表达式
        if hasattr(self.ui, "lineEdit_customize_function"):
            self.ui.lineEdit_customize_function.setText("x0**2 + x1**2")
        # 连接运行按钮
        # self.ui.run_button.clicked.connect(self.run_de_algorithm)

    # def get_algorithm_parameters(self):
    #     """从界面获取算法参数"""
    #     try:
    #         params = {
    #             "bounds": eval(self.ui.lineEdit_bounds.text()),
    #             "popSize": int(self.ui.lineEdit_popSize.text()),
    #             "mutate rate": float(self.ui.lineEdit_mutate_rate.text()),
    #             "cross rate": float(self.ui.lineEdit_cross_rate.text()),
    #             "maximum iterations": int(self.ui.lineEdit_max_iterations.text())
    #         }
    #         return params
    #     except Exception as e:
    #         self.ui.textBrowser_result_show.append(f"参数错误: {str(e)}")
    #         return None
    def get_algorithm_parameters(self):
        try:
            return {
                "bounds": eval(self.ui.lineEdit_bounds.text()),
                "popSize": int(self.ui.lineEdit_popSize.text()),
                "mutate rate": float(self.ui.lineEdit_mutate_rate.text()),
                "cross rate": float(self.ui.lineEdit_cross_rate.text()),
                "maximum iterations": int(self.ui.lineEdit_max_iterations.text())
            }
        except Exception as e:
            self.ui.textBrowser_result_show.append(f"参数错误：{str(e)}")
            return None

    def plot_custom_function_from_input(self):
        if not hasattr(self.ui, "lineEdit_customize_function"):
            self.ui.textBrowser_result_show.append("找不到自定义函数输入框")
            return

        func_str = self.ui.lineEdit_customize_function.text().strip()
        if not func_str:
            self.ui.textBrowser_result_show.append("请先输入目标函数表达式")
            return

        x, y = symbols("x y")
        try:
            expr = sympify(func_str)
            f = lambdify((x, y), expr, modules=["numpy"])

            X, Y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
            Z = f(X, Y)

            self.ax.clear()
            self.ax.contourf(X, Y, Z, cmap='plasma')
            self.ax.set_title(f"目标函数图像：{func_str}")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.canvas.draw()
        except Exception as e:
            self.ui.textBrowser_result_show.append(f"函数绘图失败：{str(e)}")

    # def run_de_algorithm(self):
    #     """运行DE算法"""
    #     params = self.get_algorithm_parameters()
    #     if params:
    #         self.ui.textBrowser_mode_show.append("正在运行DE算法...")
    #         self.ui.textBrowser_mode_show.append(f"参数: {params}")
    #
    #         # 在子线程中运行算法以避免界面卡顿
    #         self.de_thread = DEThread(params)
    #         self.de_thread.finished.connect(self.on_de_finished)
    #         self.de_thread.start()

    # def on_de_finished(self, result):
    #     """DE算法完成后的回调"""
    #     self.ui.textBrowser_mode_show.append("DE算法运行完成!")
    #     self.ui.textBrowser_mode_show.append(f"最佳解: {result['best_solution']}")
    #     self.ui.textBrowser_mode_show.append(f"最佳适应度: {result['best_fitness']}")

    # # 添加DE算法线程类
    # class DEThread(QtCore.QThread):
    #     finished = QtCore.pyqtSignal(dict)
    #
    #     def __init__(self, parameters):
    #         super().__init__()
    #         self.parameters = parameters
    #
    #     def run(self):
    #         from de import DE  # 导入你的DE算法
    #
    #         # 这里需要修改你的DE函数使其返回结果
    #         result = DE(self.parameters)
    #         self.finished.emit(result)
    def _init_de_plot(self):
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("DE 适应度曲线")
        self.ax.set_xlabel("迭代代数")
        self.ax.set_ylabel("适应度")

        # 初始化数据容器
        self.best_fitness_list = []
        self.avg_fitness_list = []

        # 将 matplotlib 的 FigureCanvas 放入 graphicsView
        scene = QtWidgets.QGraphicsScene()
        scene.addWidget(self.canvas)
        self.ui.graphicsView_result_show.setScene(scene)

    def import_external_function(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择自定义函数文件", "", "Python Files (*.py)")
        if file_path:
            self.custom_function_path = file_path
            self.ui.textBrowser_result_show.append(f"✅ 已导入函数文件：{os.path.basename(file_path)}")
            # 读取 constraint 函数并显示
            constraint_code = self.extract_constraint_function_code(file_path)
            if constraint_code:
                # self.ui.textBrowser_constraint_function.setText(constraint_code.strip())

                lines = constraint_code.split('\n')
                for i, line in enumerate(lines, 1):
                    # 简单的Python语法高亮
                    html_line = self._highlight_python_syntax(line)
                    self.ui.textBrowser_constraint_function.append(
                        f"<span style='color:gray;'>{i:3d} | </span>{html_line}"
                    )

            else:
                self.ui.textBrowser_constraint_function.setText("未找到 constraint(x) 函数")
        else:
            self.ui.textBrowser_result_show.append("❌ 取消导入")

    @staticmethod
    def extract_constraint_function_code(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        inside = False
        indent = None
        func_lines = []

        for line in lines:
            if line.strip().startswith("def constraint("):
                inside = True
                indent = len(line) - len(line.lstrip())
                func_lines.append(line)
                continue

            if inside:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() == "" or current_indent > indent:
                    func_lines.append(line)
                else:
                    break

        return "".join(func_lines) if func_lines else None

    def _highlight_python_syntax(self, line):
        """改进的Python语法高亮"""
        # 先处理字符串(避免字符串内容被错误高亮)
        line = self._highlight_strings(line)

        # Python关键字高亮
        keywords = {
            'def': 'color:#ffff7f;font-weight:bold;',
            'return': 'color:#ffff7f;font-weight:bold;',
            'if': 'color:#0000FF;font-weight:bold;',
            'else': 'color:#0000FF;font-weight:bold;',
            'elif': 'color:#0000FF;font-weight:bold;',
            'for': 'color:#0000FF;font-weight:bold;',
            'while': 'color:#0000FF;font-weight:bold;',
            'in': 'color:#0000FF;font-weight:bold;',
            'and': 'color:#ff55ff;font-weight:bold;',
            'or': 'color:#ff55ff;font-weight:bold;',
            'not': 'color:#0000FF;font-weight:bold;',
            'True': 'color:#0000FF;font-weight:bold;',
            'False': 'color:#0000FF;font-weight:bold;',
            'None': 'color:#0000FF;font-weight:bold;',
            'constraint': 'color:#800080;font-weight:bold;'  # 特别高亮约束函数名
        }

        # 处理注释
        if '#' in line:
            parts = line.split('#', 1)
            line = f"{self._highlight_keywords(parts[0], keywords)}<span style='color:#008000;'>#{parts[1]}</span>"
        else:
            line = self._highlight_keywords(line, keywords)

        return line

    def _highlight_keywords(self, text, styles):
        """高亮关键字但不影响HTML标签"""
        words = text.split()
        for i, word in enumerate(words):
            clean_word = word.strip('.,:;()[]{}<>="\'')
            if clean_word in styles:
                words[i] = word.replace(clean_word, f"<span style='{styles[clean_word]}'>{clean_word}</span>")
        return ' '.join(words)

    def _highlight_strings(self, line):
        """高亮字符串"""
        in_string = False
        result = []
        i = 0
        n = len(line)

        while i < n:
            if line[i] in ('"', "'"):
                quote = line[i]
                result.append(f"<span style='color:#800080;'>{quote}")
                i += 1
                in_string = True

                while i < n and (line[i] != quote or (i > 0 and line[i - 1] == '\\')):
                    result.append(line[i])
                    i += 1

                if i < n and line[i] == quote:
                    result.append(f"{quote}</span>")
                    i += 1
                    in_string = False
            else:
                result.append(line[i])
                i += 1

        if in_string:  # 如果字符串未闭合
            result.append("</span>")

        return ''.join(result)

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 字体自适应
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setWindowTitle("函数求解")
    # 软件图标文件导入
    icon = QIcon()
    icon.addPixmap(QPixmap(":/icon/Vector-2.svg"), QIcon.Normal, QIcon.Off)
    win.setWindowIcon(icon)

# 信号和槽机制：按键点击绑定

    # 一级菜单栏的点击绑定

    # self.action_optimize_params.triggered.connect(self.on_optimize_params)  # 迁移参考模块
    # self.action_custom_func.triggered.connect(self.on_custom_func)
    # self.action_select_algorithm.triggered.connect(self.on_select_algorithm)
    # win.ui.action_paramater_optimize.triggered.connect(win.hide_menu_paramater_optimize)
    # win.ui.action_customize_function.triggered.connect(win.hide_menu_customize_function)
    # win.ui.menu_paramater_optimize.triggered.connect(win.hide_menu_paramater_optimize)
    # win.ui.menu_customize_function.triggered.connect(win.hide_menu_customize_function)

    # 隐藏与显示代码 槽函数
    # error action仅可绑定一个function，下方注释代码弃用，但为 debug参考。
    # win.ui.action_paramater_optimize.triggered.connect(
    #     lambda: win.toggle_menu(
    #         win.ui.verticalLayout_2,
    #         win.ui.verticalLayout_4,
    #         win.ui.action_paramater_optimize
    #     ),
    #     win.textBrower_show(
    #         win.ui.action_paramater_optimize
    #     )
    #     # lambda: win.textBrower_show(
    #     #     win.ui.action_paramater_optimize
    #     # )
    # )
    #
    # win.ui.action_customize_function.triggered.connect(
    #     lambda: win.toggle_menu(
    #         win.ui.verticalLayout_4,
    #         win.ui.verticalLayout_2,
    #         win.ui.action_customize_function),
    #             win.textBrower_show(
    #                 win.ui.action_customize_function
    # )
    #     # ),
    #     # lambda: win.textBrower_show(
    #     #     win.ui.action_customize_function
    #     # )
    # )
    win.ui.action_paramater_optimize.triggered.connect(win.handle_parameter_optimize)
    win.ui.action_customize_function.triggered.connect(win.handle_custom_function)

    # qtextbrower的font size方法
    # win.setup_textbrowser_font()

    win.ui.pushButton_import_function.clicked.connect(win.import_external_function)

    from qt_material import apply_stylesheet
    # apply_stylesheet(app, theme='dark_teal.xml')
    extra = {

        # Density Scale
        'density_scale': '-2',
    }
    apply_stylesheet(app, theme='dark_cyan.xml', invert_secondary=True, extra=extra)
    win.show()
    sys.exit(app.exec_())


