# 算法参数设置及初始化

class DEParameterManager:
    def __init__(self, ui):
        self.ui = ui

    def init_default_parameters(self):
        """初始化默认参数到界面输入框"""
        self.ui.lineEdit_bounds.setText("[(-1, 1), (-1, 1)]")
        self.ui.lineEdit_popSize.setText("10")
        self.ui.lineEdit_mutate_rate.setText("0.5")
        self.ui.lineEdit_cross_rate.setText("0.8")
        self.ui.lineEdit_max_iterations.setText("20")

        # if hasattr(self.ui, "lineEdit_customize_function"):
        #     self.ui.lineEdit_customize_function.setText("x0**2 + x1**2")

    def get_parameters(self):
        """从界面获取参数字典"""
        try:
            params = {
                "bounds": eval(self.ui.lineEdit_bounds.text()),
                "popSize": int(self.ui.lineEdit_popSize.text()),
                "mutate rate": float(self.ui.lineEdit_mutate_rate.text()),
                "cross rate": float(self.ui.lineEdit_cross_rate.text()),
                "maximum iterations": int(self.ui.lineEdit_max_iterations.text())
            }
            return params
        except Exception as e:
            if hasattr(self.ui, "textBrowser_operation_history"):
                self.ui.textBrowser_operation_history.append(f"❌ 参数错误：{str(e)}")
            return None

    # def get_custom_function_expr(self):
    #     """读取自定义函数表达式（如果有）"""
    #     try:
    #         return self.ui.lineEdit_customize_function.text()
    #     except:
    #         return None
