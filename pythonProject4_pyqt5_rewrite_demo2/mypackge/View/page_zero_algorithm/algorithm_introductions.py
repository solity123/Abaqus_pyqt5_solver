"""page_algorithm 下的tabWidget下的textBrowser_algorithm_introduce中展示的 算法介绍模块"""


class AlgorithmIntroductions:
    """算法介绍内容管理器"""

    def __init__(self):
        self.introductions = {
            "DE": self.de_introduction(),
            "PSO": self.pso_introduction(),
            "GA": self.ga_introduction(),
            # 添加更多算法...
        }

    def get_introduction(self, algorithm_key):
        """获取指定算法的介绍内容"""
        return self.introductions.get(algorithm_key, "<p>该算法介绍暂未提供</p>")

    def de_introduction(self):
        """差分进化算法介绍"""
        return """
            <h2>差分进化算法 (Differential Evolution, DE)</h2>
            <p><b>差分进化算法</b>是一种基于群体的随机优化算法，由Storn和Price于1997年提出。它主要用于解决连续优化问题。</p>

            <h3>主要步骤：</h3>
            <ol>
                <li><b>初始化种群</b>：随机生成初始种群</li>
                <li><b>变异</b>：对每个个体，选择三个不同的个体，生成变异个体</li>
                <li><b>交叉</b>：将变异个体与当前个体进行交叉操作，生成试验个体</li>
                <li><b>选择</b>：比较试验个体和当前个体的适应度，选择较优者进入下一代</li>
            </ol>

            <h3>核心公式：</h3>
            <p>变异操作：<br>
            <i>v<sub>i,G+1</sub> = x<sub>r1,G</sub> + F × (x<sub>r2,G</sub> - x<sub>r3,G</sub>)</i></p>

            <p>交叉操作：<br>
            <i>u<sub>j,i,G+1</sub> = 
                <span style="color:blue;">v<sub>j,i,G+1</sub></span> if rand<sub>j</sub> ≤ CR or j = j<sub>rand</sub>
                <br><span style="color:green;">x<sub>j,i,G</sub></span> otherwise
            </i></p>

            <h3>参数说明：</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>参数</th>
                    <th>含义</th>
                    <th>常用值</th>
                </tr>
                <tr>
                    <td>NP</td>
                    <td>种群大小</td>
                    <td>5D-10D (D为维度)</td>
                </tr>
                <tr>
                    <td>F</td>
                    <td>缩放因子</td>
                    <td>0.4-1.0</td>
                </tr>
                <tr>
                    <td>CR</td>
                    <td>交叉概率</td>
                    <td>0.1-1.0</td>
                </tr>
            </table>

            <h3>应用领域：</h3>
            <ul>
                <li>工程优化设计</li>
                <li>机器学习参数优化</li>
                <li>电力系统调度</li>
                <li>图像处理</li>
            </ul>

            <div style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #36c;">
                <p><b>特点总结：</b> 结构简单、全局搜索能力强、参数少、易于实现。</p>
            </div>

            <p>更多信息请参考：<a href="https://en.wikipedia.org/wiki/Differential_evolution">Wikipedia - Differential Evolution</a></p>
        """

    def pso_introduction(self):
        """粒子群优化算法介绍"""
        return "<h2>粒子群优化算法 (PSO)</h2><p>粒子群优化算法介绍内容...</p>"

    def ga_introduction(self):
        """遗传算法介绍"""
        return "<h2>遗传算法 (GA)</h2><p>遗传算法介绍内容...</p>"