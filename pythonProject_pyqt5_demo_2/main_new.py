import sys
from mypackge.ui.MainWindow_refine import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # UI初始化
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化菜单状态
        self._init_menu_states()

        # 窗口尺寸设置
        self._setup_window_size()

    def _setup_window_size(self):
        """设置窗口初始大小"""
        screen = QApplication.primaryScreen().geometry()
        print(f"Screen height {screen.height()}")
        print(f"Screen width {screen.width()}")
        self.resize(int(screen.width() * 0.65), int(screen.height() * 0.8))

    def _init_menu_states(self):
        """初始化菜单显示状态"""
        # 添加存在性检查
        if hasattr(self.ui, 'verticalLayout_2'):
            self._set_layout_visibility(self.ui.verticalLayout_2, True)
        if hasattr(self.ui, 'verticalLayout_4'):
            self._set_layout_visibility(self.ui.verticalLayout_4, False)
        if hasattr(self.ui, 'action_customize_function'):
            self.ui.action_customize_function.setChecked(True)
        if hasattr(self.ui, 'action_paramater_optimize'):
            self.ui.action_paramater_optimize.setChecked(True)

    def _set_layout_visibility(self, layout, visible):
        """
        设置布局中所有控件的可见性
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setVisible(visible)

    def toggle_menu(self, menu_layout, other_layout, action):
        """
        更安全的切换方法
        """
        try:
            if not all([menu_layout, other_layout, action]):
                return

            # 防止递归
            if getattr(self, '_switching', False):
                return
            self._switching = True

            # 切换菜单布局的可见性
            current_visible = not menu_layout.isVisible()
            self._set_layout_visibility(menu_layout, current_visible)
            action.setChecked(current_visible)

            # 隐藏其他布局
            if other_layout.isVisible():
                self._set_layout_visibility(other_layout, False)
                if other_layout == getattr(self.ui, 'verticalLayout_2', None):
                    getattr(self.ui, 'action_customize_function', None).setChecked(False)
                else:
                    getattr(self.ui, 'action_paramater_optimize', None).setChecked(False)

        except Exception as e:
            print(f"切换菜单错误: {e}")
        finally:
            self._switching = False


if __name__ == '__main__':
    # 先创建QApplication再设置属性
    app = QApplication(sys.argv)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    try:
        win = MainWindow()
        win.setWindowTitle("函数求解")

        # 更安全的图标加载
        try:
            icon = QIcon()
            if icon.addPixmap(QPixmap(":/icon/Vector-2.svg")):
                win.setWindowIcon(icon)
        except:
            print("图标加载失败，使用默认图标")

        # 连接信号槽
        if hasattr(win.ui, 'action_paramater_optimize'):
            win.ui.action_paramater_optimize.triggered.connect(
                lambda: win.toggle_menu(
                    getattr(win.ui, 'verticalLayout_4', None),
                    getattr(win.ui, 'verticalLayout_2', None),
                    win.ui.action_paramater_optimize
                )
            )

        if hasattr(win.ui, 'action_customize_function'):
            win.ui.action_customize_function.triggered.connect(
                lambda: win.toggle_menu(
                    getattr(win.ui, 'verticalLayout_2', None),
                    getattr(win.ui, 'verticalLayout_4', None),
                    win.ui.action_customize_function
                )
            )

        win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)