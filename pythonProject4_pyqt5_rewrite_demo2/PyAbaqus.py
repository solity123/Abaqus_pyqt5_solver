# 逻辑部分
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import matplotlib
from mypackge.View.main_window import MainWindow

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体（SimHei）
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 高分辨率下字体自适应
app = QApplication(sys.argv)
win = MainWindow()
win.setWindowTitle("PyAbaqus")  # 软件名称
win.show()
sys.exit(app.exec_())
