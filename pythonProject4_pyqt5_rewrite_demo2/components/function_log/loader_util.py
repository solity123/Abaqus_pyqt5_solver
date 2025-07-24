from components.function_log import load_functions_from_file


def get_objective_functions_map():
    """
    从 JSON 加载所有目标函数，返回字典形式：
    {name: (code, latex, filepath)}
    """
    objective_function_map = {}
    try:
        functions = load_functions_from_file()
        for func in functions:
            if len(func) >= 4:
                name, latex, code, filepath = func[0], func[1], func[2], func[3] if len(func) > 3 else None
                objective_function_map[name] = (code, latex, filepath)
    except Exception as e:
        print(f"❌ 加载函数失败: {e}")
    return objective_function_map
