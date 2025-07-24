import os
import re
import json
import hashlib

# 保存路径
SAVE_PATH = os.path.join(os.path.dirname(__file__), '../saved_functions.json')


def generate_function_id(func_data):
    name = func_data[0]
    path = func_data[3] if len(func_data) > 3 else ''
    return hashlib.md5(f"{name}|{path}".encode('utf-8')).hexdigest()


def extract_functions_from_file(file_path):
    """从Python文件中提取函数名、latex表达式、源码"""
    with open(file_path, 'r', encoding='utf-8') as f:
        code_lines = f.readlines()

    functions = []
    current_latex = None
    current_code = []
    recording = False
    func_name = None

    for i, line in enumerate(code_lines):
        stripped_line = line.strip()

        if stripped_line.startswith('# latex:'):
            # ⛔ 修复关键逻辑：遇到新 latex 前，先保存前一个函数
            if recording and current_latex and current_code and func_name:
                func_code = ''.join(current_code)
                functions.append([func_name, current_latex, func_code.strip(), file_path])

            current_latex = stripped_line[len('# latex:'):].strip()
            recording = False
            func_name = None
            current_code = []

        elif stripped_line.startswith('def '):
            if recording and current_latex and current_code and func_name:
                func_code = ''.join(current_code)
                functions.append([func_name, current_latex, func_code.strip(), file_path])
                current_code = []

            match = re.match(r'def\s+(\w+)', stripped_line)
            if match:
                func_name = match.group(1)
                recording = True
                current_code = [line]
            else:
                recording = False
                current_code = []

        elif recording:
            current_code.append(line)

    # ✅ 文件结尾处理最后一个函数
    if recording and current_latex and current_code and func_name:
        func_code = ''.join(current_code)
        functions.append([func_name, current_latex, func_code.strip(), file_path])

    print(f"从文件 {file_path} 中提取到 {len(functions)} 个函数")
    for i, func in enumerate(functions, 1):
        print(f"函数 {i}: {func[0]} - {func[1]}")

    return functions


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
        if len(func) < 5:
            func.append(generate_function_id(func))

    # 加载现有函数
    old_functions = load_functions_from_file()

    # 创建ID到函数的映射
    old_func_map = {func[4]: func for func in old_functions if len(func) > 4}

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


def save_functions_to_file(functions):
    try:
        # 为每个函数添加唯一ID
        for func in functions:
            if len(func) < 5:  # 如果没有ID
                func.append(generate_function_id(func))

        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(functions, f, indent=4, ensure_ascii=False)
        print(f"✅ 成功保存 {len(functions)} 个函数到 {SAVE_PATH}")
        print("📝 保存函数内容: ", json.dumps(functions, indent=2))
    except Exception as e:
        print("❌ 保存失败：", e)


def load_functions_from_file():
    if not os.path.exists(SAVE_PATH):
        return []
    try:
        with open(SAVE_PATH, 'r', encoding='utf-8') as f:
            functions = json.load(f)

            # 确保旧数据也有ID
            for func in functions:
                if len(func) < 5:
                    func.append(generate_function_id(func))

            return functions
    except Exception as e:
        print("❌ 加载失败：", e)
        return []
