from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from mypackge.ui.dialog_window import Ui_Dialog
from mypackge.View.dialog_win.listwidget_base import FormulaListWidget
from PyQt5.QtCore import QEvent, pyqtSignal, QObject

import os
import sys
import subprocess
import platform

from components.function_log import (
    extract_functions_from_file,
    save_functions_to_file,
    load_functions_from_file,
    generate_function_id
)

import time
import threading


def update_functions_from_file(file_path):
    """更新或添加文件中的函数到JSON"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return

    # 提取文件中的函数
    updated_functions = extract_functions_from_file(file_path)
    if not updated_functions:
        print(f"文件 {file_path} 中没有找到符合格式的函数")
        return

    # 为每个新函数生成ID
    for func in updated_functions:
        if len(func) < 5:  # 如果还没有ID
            func.append(generate_function_id(func))

    # 加载现有函数
    old_functions = load_functions_from_file()

    # 创建ID到函数的映射
    old_func_map = {func[4]: func for func in old_functions}

    # 更新或添加函数
    for new_func in updated_functions:
        func_id = new_func[4]
        if func_id in old_func_map:
            # 更新现有函数
            old_func = old_func_map[func_id]
            # 保留原始名称和文件路径（如果存在）
            if len(old_func) > 0:
                new_func[0] = old_func[0]  # 保留原始名称
            if len(old_func) > 3 and old_func[3]:
                new_func[3] = old_func[3]  # 保留原始文件路径
            old_func_map[func_id] = new_func
        else:
            # 添加新函数
            old_func_map[func_id] = new_func

    # 保存更新后的函数列表
    updated_list = list(old_func_map.values())
    save_functions_to_file(updated_list)
    print(f"🔄 已更新文件 {file_path} 中的 {len(updated_functions)} 个函数")


class ObjectiveFunctionDialog(QDialog):

    update_list_requested = pyqtSignal(str)
    confirmed = pyqtSignal()  # ok
    cancelled = pyqtSignal()  # cancel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.custom_list_widget = None

        self.function_map = {}
        self.objective_function_map = {}
        self.rewrite_list_widget()
        self.__signal_to_slot__()

        self.load_functions_into_list()

    def rewrite_list_widget(self):
        self.custom_list_widget = FormulaListWidget(self)
        self.ui.verticalLayout.insertWidget(0, self.custom_list_widget)
        self.ui.listWidget.deleteLater()
        self.ui.listWidget = self.custom_list_widget

    def __signal_to_slot__(self):
        self.ui.pushButton_view.clicked.connect(self.view_functions)
        self.ui.pushButton_add.clicked.connect(self.import_and_save_functions)
        self.ui.pushButton_edit.clicked.connect(self.edit_function_file)
        self.update_list_requested.connect(self.update_function_list)
        self.ui.buttonBox_dialog.accepted.connect(self.on_accept_clicked)
        self.ui.buttonBox_dialog.rejected.connect(self.on_reject_clicked)
        self.ui.pushButton_delete.clicked.connect(self.delete_selected_function)

    def on_accept_clicked(self):
        self.confirmed.emit()
        self.close()

    def on_reject_clicked(self):
        self.cancelled.emit()
        self.close()

    def load_functions_into_list(self):
        self.custom_list_widget.clear_formulas()
        """从 JSON 文件加载函数并显示"""
        try:
            functions = load_functions_from_file()
            for func in functions:
                # 现在每个函数有5个元素: [name, latex, code, filepath, id]
                if len(func) >= 4:  # 确保至少包含前4个元素
                    name = func[0]
                    latex = func[1]
                    code = func[2]
                    filepath = func[3] if len(func) > 3 else None

                    self.custom_list_widget.add_formula(name, latex, code, filepath)
                    self.function_map[latex] = (name, code)
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"读取函数失败：{e}")

    def view_functions(self):
        """显示当前选中函数的代码"""
        try:
            info = self.custom_list_widget.get_selected_formula()
            if info:
                # info 现在包含5个元素，但我们只需要前3个
                name = info[0]
                latex_str = info[1]
                code_text = info[2]
                self.ui.textEdit.setPlainText(code_text)
        except Exception as e:
            print("查看函数失败:", e)

    def import_and_save_functions(self):
        """导入 Python 文件函数并保存到 JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择包含目标函数的 Python 文件",
            "",
            "Python Files (*.py)"
        )
        if file_path:
            try:
                new_functions = extract_functions_from_file(file_path)
                if new_functions:
                    old_functions = load_functions_from_file()
                    combined = old_functions + [
                        f for f in new_functions
                        if not any(f[1] == old[1] for old in old_functions)  # 避免 LaTeX 重复
                    ]
                    save_functions_to_file(combined)

                    # 重新加载 UI 列表
                    self.custom_list_widget.clear()
                    self.load_functions_into_list()

                    QMessageBox.information(self, "导入成功", f"导入了 {len(new_functions)} 个函数")
                else:
                    QMessageBox.warning(self, "无函数", "未识别到符合格式的函数")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"出错：{e}")

    def edit_function_file(self):
        """使用 IDLE 编辑源代码文件，并在修改后同步更新 JSON 和列表"""
        try:
            info = self.custom_list_widget.get_selected_formula()
            if info and len(info) >= 4:  # 确保有足够的元素
                filepath = info[3] if len(info) > 3 else None
                if filepath and os.path.exists(filepath):
                    # 获取初始修改时间
                    last_modified = os.path.getmtime(filepath)

                    def open_editor():
                        python_exe = sys.executable
                        idle_path = os.path.join(os.path.dirname(python_exe), 'idle.pyw')
                        if os.path.exists(idle_path):
                            subprocess.Popen([python_exe, idle_path, filepath])
                        else:
                            subprocess.Popen([python_exe, '-m', 'idlelib', filepath])

                    def monitor_file_change():
                        while True:
                            time.sleep(1.5)
                            try:
                                new_time = os.path.getmtime(filepath)
                                if new_time != last_modified:
                                    print("🔄 文件已修改，请求更新函数列表...")
                                    # 使用信号通知主线程更新
                                    self.update_list_requested.emit(filepath)
                                    break
                            except Exception as e:
                                print("文件监测错误：", e)
                                break

                    threading.Thread(target=monitor_file_change, daemon=True).start()
                    open_editor()
                else:
                    QMessageBox.warning(self, "无法打开", "未找到原始文件路径或文件不存在。")
            else:
                QMessageBox.warning(self, "未选择", "请先选择一个函数。")
        except Exception as e:
            QMessageBox.critical(self, "打开错误", f"打开文件出错：\n{str(e)}")

    def event(self, event):
        """当窗口重新激活时尝试更新函数"""
        if event.type() == QEvent.WindowActivate:
            # 获取当前选中函数的文件路径并更新
            info = self.custom_list_widget.get_selected_formula()
            if info and len(info) >= 4:
                file_path = info[3]
                if file_path and os.path.exists(file_path):
                    update_functions_from_file(file_path)
                    # 重新刷新界面
                    self.custom_list_widget.clear()
                    self.load_functions_into_list()
        return super().event(event)

    def update_function_list(self, filepath):
        """在文件修改后更新函数列表"""
        if threading.current_thread() is not threading.main_thread():
            print("警告: 在非主线程尝试更新UI")
            return
        try:
            update_functions_from_file(filepath)

            # 清空所有缓存并重新加载
            self.custom_list_widget.clear_formulas()
            self.function_map.clear()
            self.load_functions_into_list()

        except Exception as e:
            print(f"更新函数列表失败: {e}")

    def delete_selected_function(self):
        info = self.custom_list_widget.get_selected_formula()
        if not info:
            QMessageBox.warning(self, "未选择", "请先选择一个要删除的函数。")
            return

        name, latex_str, code_text, filepath = info[:4]
        confirm = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除函数 '{name}' 吗？\n该操作将从 JSON 和源文件中删除此函数。",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        # 删除 JSON 中的函数
        functions = load_functions_from_file()
        filtered = [f for f in functions if not (f[1] == latex_str and f[3] == filepath)]
        save_functions_to_file(filtered)

        # 删除 Python 源码中的该函数定义
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                new_lines = []
                skip = False
                inside_target = False

                for i, line in enumerate(lines):
                    if line.strip().startswith("# latex:") and latex_str in line:
                        skip = True
                        inside_target = True
                        continue
                    if inside_target and line.strip().startswith("def "):
                        continue  # 跳过 def 行
                    if inside_target and not line.startswith(" ") and not line.startswith("\t"):
                        skip = False
                        inside_target = False
                    if not skip:
                        new_lines.append(line)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

                QMessageBox.information(self, "删除成功", f"函数 '{name}' 已成功删除。")
            except Exception as e:
                QMessageBox.critical(self, "删除失败", f"从源文件中删除失败：{e}")

        # 刷新 UI
        self.custom_list_widget.clear_formulas()
        self.load_functions_into_list()


