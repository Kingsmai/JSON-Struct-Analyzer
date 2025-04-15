import os
import json
from numbers import Number

json_file_list = []

# Walk through all files in the data directory
for root, dirs, files in os.walk('data'):
    for file in files:
        if file.endswith('.json'):
            json_file_list.append(os.path.join(root, file))

data_pattern = {}


def create_entry(value):
    """根据值的类型创建新的统计条目"""
    current_type = type(value) if value is not None else type(None)
    entry = {
        'type': current_type,
        'count': 0,
    }

    if isinstance(value, bool):
        entry['possible_values'] = set()
    elif isinstance(value, Number) and not isinstance(value, bool):
        entry['max_value'] = value
        entry['min_value'] = value
    elif isinstance(value, str):
        entry['max_length'] = len(value)
        entry['min_length'] = len(value)
        entry['possible_values'] = set()
    elif isinstance(value, (list, dict)):
        entry['max_length'] = len(value)
        entry['min_length'] = len(value)
    elif value is None:
        entry['possible_values'] = set()

    return entry


def update_entry(entry, value):
    """更新现有条目的统计信息"""
    entry['count'] += 1

    if isinstance(value, bool):
        entry['possible_values'].add(value)
        if len(entry['possible_values']) > 10:
            entry['possible_values'] = set(list(entry['possible_values'])[:10])
    elif isinstance(value, Number) and not isinstance(value, bool):
        entry['max_value'] = max(entry['max_value'], value)
        entry['min_value'] = min(entry['min_value'], value)
    elif isinstance(value, str):
        str_len = len(value)
        entry['max_length'] = max(entry['max_length'], str_len)
        entry['min_length'] = min(entry['min_length'], str_len)
        if len(entry['possible_values']) < 10 and value not in entry['possible_values']:
            entry['possible_values'].add(value)
    elif isinstance(value, (list, dict)):
        coll_len = len(value)
        entry['max_length'] = max(entry['max_length'], coll_len)
        entry['min_length'] = min(entry['min_length'], coll_len)
    elif value is None:
        entry['possible_values'].add(None)


def analyze_value(value, path):
    """递归分析数据结构并更新模式统计"""
    # 获取或初始化当前路径的条目列表
    if path not in data_pattern:
        data_pattern[path] = []

    current_type = type(value) if value is not None else type(None)
    found_entry = None

    # 查找是否存在当前类型的条目
    for entry in data_pattern[path]:
        if entry['type'] == current_type:
            found_entry = entry
            break

    # 如果不存在，创建新条目并添加到列表
    if not found_entry:
        new_entry = create_entry(value)
        data_pattern[path].append(new_entry)
        found_entry = new_entry

    # 更新条目统计
    update_entry(found_entry, value)

    # 递归处理嵌套结构
    if isinstance(value, dict):
        for k, v in value.items():
            new_path = f"{path}.{k}" if path else k
            analyze_value(v, new_path)
    elif isinstance(value, list):
        for item in value:
            new_path = f"{path}.[]" if path else ".[]"
            analyze_value(item, new_path)


# 处理所有JSON文件
for json_file in json_file_list:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        analyze_value(data, 'root')

# 后处理：转换类型名称和集合为列表
for path in data_pattern:
    for entry in data_pattern[path]:
        # 转换类型对象为类型名称
        if isinstance(entry['type'], type):
            entry['type'] = 'null' if entry['type'] is type(
                None) else entry['type'].__name__

        # 转换集合为列表并限制可能值的数量
        if 'possible_values' in entry:
            entry['possible_values'] = list(entry['possible_values'])[:10]

# 创建输出目录
if not os.path.exists('output'):
    os.makedirs('output')

# 保存模式分析结果
with open('output/data_pattern.json', 'w', encoding='utf-8') as f:
    json.dump(data_pattern, f, ensure_ascii=False, indent=4)
