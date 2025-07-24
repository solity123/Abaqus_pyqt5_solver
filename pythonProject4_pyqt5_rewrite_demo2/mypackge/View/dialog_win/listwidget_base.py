from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import io
from PyQt5.QtCore import Qt
from matplotlib import rcParams


class FormulaListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formula_data = []  # 存储 (name, latex_str, code_text)
        self.max_image_size = (250, 40)  # 最大图像尺寸

    def add_formula(self, name: str, latex_str: str, code_text: str, filepath=None):
        # 设置字体和渲染参数（清晰度）
        rcParams.update({
            "text.usetex": False,
            "font.family": "serif",
            "mathtext.fontset": "stix",  # 更接近 LaTeX 数学字体
            "font.size": 20,
        })

        fig, ax = plt.subplots(figsize=(4, 0.6), dpi=200)
        fig.patch.set_facecolor('none')
        ax.axis('off')
        ax.text(0.5, 0.5, f"${latex_str}$", fontsize=14, ha='center', va='center')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        plt.close(fig)

        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())

        # 高分辨率缩放显示（抗锯齿）
        pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; padding-bottom: 5px;")

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        layout.addWidget(name_label)
        layout.addWidget(image_label)
        widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

        self.formula_data.append((name, latex_str, code_text, filepath))

    def get_selected_formula(self):
        """
        返回当前选中项的信息：(name, latex_str, code_text)
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.formula_data):
            return self.formula_data[current_row]
        return None

    def clear_formulas(self):
        self.clear()
        self.formula_data.clear()
