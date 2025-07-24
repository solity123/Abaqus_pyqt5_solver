from PyQt5.QtWidgets import QWidget, QApplication, QAction, QDialogButtonBox
from mypackge.ui.mainwin_try import Ui_Form
import sys
from mypackge.View.page_zero_algorithm.algorithm_introductions import AlgorithmIntroductions
from mypackge.logic.DE_algorithm.de_controller import DEController
from mypackge.View.page_zero_algorithm.algorithm_parameter_manager import DEParameterManager
from mypackge.View.dialog_win.objective_function_popup import ObjectiveFunctionDialog

from components.function_log.loader_util import get_objective_functions_map


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # 继承QMainWindow 这一father 的__init__()方法
        # 初始化ui.py文件 逻辑和界面分离
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.adjustSize()

        # 初始化 实例变量
        self.objective_function_map = None

        # 主窗口大小设置
        self.__initSize__()

        # 模块实例化
        self.__initModules__()

        # 初始化UI状态
        self.initialize_ui()

        # 信号与槽机制 连接
        self.__SignalToSlot__()

    def __initSize__(self):
        """获取显示器分辨率,初始化MainWindow窗口大小"""
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()
        print("Screen height {}".format(self.screenheight))
        print("Screen width {}".format(self.screenwidth))
        self.width = int(self.screenwidth * 0.8)
        self.height = int(self.screenheight * 0.83)
        self.resize(self.width, self.height)

    def __initModules__(self):
        # 初始化算法介绍模块
        self.algorithm_intros = AlgorithmIntroductions()

        # 初始化算法 params
        self.param_manager = DEParameterManager(self.ui)
        # 初始化DE算法控制模块
        self.de_controller = DEController()
        # 初始化 目标函数弹出窗口模块
        # self.dialog =

        # 初始化 目标函数 存储
        self.objective_function_map = {}

    def initialize_ui(self):
        """初始化UI元素的状态"""
        # 设置初始页面
        self.clicked_pushbutton_navigation_sidebar(0)

        # 初始化标签文本
        self.update_algorithm_label()

        # 初始化算法介绍
        self.update_algorithm_introduction()

        # DE 算法 启停 按钮初始化
        # 设置按钮文本
        self.ui.buttonBox_running.button(QDialogButtonBox.Ok).setText("开始")
        self.ui.buttonBox_running.button(QDialogButtonBox.Cancel).setText("停止")
        # 算法 params 初始化
        self.param_manager.init_default_parameters()

        # 目标函数的 下拉框 初始化
        self.load_objective_functions_to_combobox()

    def __SignalToSlot__(self):
        """信号与槽机制 的连接"""

        """navigation_sidebar"""
        # 侧边导航栏 基础界面切换
        self.ui.pushButton_algorithm.clicked.connect(lambda: self.clicked_pushbutton_navigation_sidebar(0))
        self.ui.pushButton_function.clicked.connect(lambda: self.clicked_pushbutton_navigation_sidebar(1))
        self.ui.pushButton_more.clicked.connect(lambda: self.clicked_pushbutton_navigation_sidebar(2))
        """page_zero_algorithm"""
        # stackedWidget index:0 QGroupBox:groupBox_select_algorithm

        self.ui.comboBox_algorithm.activated.connect(self.on_algorithm_changed)

        """DE算法"""
        """DE算法的结果msg传递"""
        self.de_controller.progress_signal.connect(self.handle_de_progress)
        self.de_controller.finished_signal.connect(self.handle_de_finished)
        # DE 算法 运行与停止
        self.ui.buttonBox_running.accepted.connect(self.run_de_algorithm)
        self.ui.buttonBox_running.rejected.connect(self.stop_de_algorithm)

        # self.de_controller.progress_signal.connect(self._on_progress)  # debug 验证

    # def _on_progress(self, info):  # debug
    #     if isinstance(info, dict):
    #         self.ui.textBrowser_operation_history.append(info.get("message", ""))
    #     else:
    #         self.ui.textBrowser_operation_history.append(str(info))

        """目标函数弹窗 """
        self.ui.toolButton_object_fun_input.clicked.connect(self.show_objective_dialog)
        # 目标函数 combobox 下拉框选中 传递
        self.ui.comboBox_object_fun.currentIndexChanged.connect(self.on_objective_function_changed)

    def clicked_pushbutton_navigation_sidebar(self, index=0):
        self.ui.stackedWidget.setCurrentIndex(index)

    def on_algorithm_changed(self):
        """当算法选择改变时更新标签和介绍"""
        self.update_algorithm_label()
        self.update_algorithm_introduction()

    def update_algorithm_label(self):
        # current_text = self.ui.comboBox_algorithm.currentText()
        # self.ui.label_algorithm_text.setText("当前选择：{}算法".format(current_text))
        """更新算法标签显示当前选择的算法"""
        current_text = self.ui.comboBox_algorithm.currentText()

        # 使用HTML设置高亮样式
        formatted_text = (
            "当前选择：<span style='"
            "background-color: #FFF59D; "  # 柔和的黄色背景
            "font-weight: bold; "
            "color: #E65100; "
            "padding: 2px 6px; "
            "border-radius: 4px;"
            "border: 1px solid #FBC02D;"
            "'>"
            f"{current_text}"
            "</span>算法"
        )

        self.ui.label_algorithm_text.setText(formatted_text)

    def update_algorithm_introduction(self):
        """更新算法介绍内容"""
        # 获取当前选中的算法名称
        current_algorithm = self.ui.comboBox_algorithm.currentText()
        self.ui.tabWidget.setCurrentIndex(0)
        # 简化算法名称作为键（例如："差分进化算法(DE)" -> "DE"）
        algorithm_key = ""
        if "DE" in current_algorithm:
            algorithm_key = "DE"
        elif "PSO" in current_algorithm:
            algorithm_key = "PSO"
        elif "GA" in current_algorithm:
            algorithm_key = "GA"

        # 获取算法介绍内容
        introduction_html = self.algorithm_intros.get_introduction(algorithm_key)
        # 设置到文本浏览器
        self.ui.textBrowser_algorithm_introduce.setHtml(introduction_html)

    def handle_de_progress(self, data):
        msg = ""
        if "generation" in data and data["generation"] >= 0:
            msg += f"📈 第 {data['generation']} 代 - 最优适应度：{data['best_fitness']:.4f}，平均适应度：{data['avg_fitness']:.4f}"
        if "message" in data:
            msg += f"\n{data['message']}"
        self.ui.textBrowser_operation_history.append(msg)

    def handle_de_finished(self, result):
        if result.get("status") == "ok":
            self.ui.textBrowser_operation_history.append(
                f"✅ 运行完成！最优解：{result['best_solution']}\n"
                f"最优适应度：{result['best_fitness']:.4f}")
        elif result.get("status") == "stopped":
            self.ui.textBrowser_operation_history.append("⏹️ 算法已手动终止。")
        else:
            self.ui.textBrowser_operation_history.append(f"❌ 出错：{result.get('message', '未知错误')}")

    def run_de_algorithm(self):
        params = self.param_manager.get_parameters()
        # func_expr = self.param_manager.get_custom_function_expr()

        # if params is None or func_expr is None:
        #     return
        if params is None:
            return

        self.ui.textBrowser_operation_history.append("🚀 差分进化开始运行...")
        self.de_controller.run(params=params)

    def stop_de_algorithm(self):
        """手动停止差分进化"""
        self.de_controller.stop()
        self.ui.textBrowser_operation_history.append("🛑 请求停止算法运行...")

    def show_objective_dialog(self):
        dialog = ObjectiveFunctionDialog(self)
        dialog.confirmed.connect(lambda: self.ui.textBrowser_operation_history.append("✅ 用户确认了目标函数选择"))
        dialog.confirmed.connect(self.load_objective_functions_to_combobox)
        dialog.cancelled.connect(lambda: self.ui.textBrowser_operation_history.append("❎ 用户取消了目标函数选择"))
        dialog.show()

    def load_objective_functions_to_combobox(self):
        self.ui.comboBox_object_fun.clear()
        self.objective_function_map = get_objective_functions_map()
        for name in self.objective_function_map:
            self.ui.comboBox_object_fun.addItem(name)

    def on_objective_function_changed(self, index):
        name = self.ui.comboBox_object_fun.currentText()
        if name and name in self.objective_function_map:
            code, latex, filepath = self.objective_function_map[name]
            self.ui.textBrowser_operation_history.append(f"🎯 当前目标函数已切换为：{name}")
