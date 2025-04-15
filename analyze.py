import os
import json

from numbers import Number

json_file_list = []

# Walk through all file in data directory
for root, dirs, files in os.walk('data'):
    for file in files:
        if file.endswith('.json'):
            json_file_list.append(os.path.join(root, file))

data_pattern = {}


def analyze_value(value, path):
    """递归分析数据结构并更新模式统计"""
    # 处理当前路径的统计
    current_type = type(value) if value is not None else type(None)

    if path not in data_pattern:
        # 初始化新路径的统计
        data_pattern[path] = {
            'type': current_type,
            'count': 1
        }

        if isinstance(value, bool):
            data_pattern[path]['possible_values'] = {value}
        elif isinstance(value, Number) and not isinstance(value, bool):
            data_pattern[path].update({
                'max_value': value,
                'min_value': value
            })
        elif isinstance(value, str):
            data_pattern[path].update({
                'max_length': len(value),
                'min_length': len(value),
                'possible_values': {value}
            })
        elif isinstance(value, (list, dict)):
            data_pattern[path].update({
                'max_length': len(value),
                'min_length': len(value)
            })
        elif value is None:
            data_pattern[path]['possible_values'] = {None}
    else:
        # 更新现有路径统计
        entry = data_pattern[path]
        entry['count'] += 1

        # 类型一致性检查（None特殊处理）
        if not (isinstance(value, entry['type']) or
                (value is None and entry['type'] is type(None))):
            return

        # 根据类型更新统计
        if entry['type'] == bool:
            entry['possible_values'].add(value)
            entry['possible_values'] = set(list(entry['possible_values'])[:10])
        elif entry['type'] in (int, float):
            entry['max_value'] = max(entry['max_value'], value)
            entry['min_value'] = min(entry['min_value'], value)
        elif entry['type'] == str:
            str_len = len(value)
            entry['max_length'] = max(entry['max_length'], str_len)
            entry['min_length'] = min(entry['min_length'], str_len)
            if len(entry['possible_values']) < 10 and value not in entry['possible_values']:
                entry['possible_values'].add(value)
        elif entry['type'] in (list, dict):
            coll_len = len(value)
            entry['max_length'] = max(entry['max_length'], coll_len)
            entry['min_length'] = min(entry['min_length'], coll_len)

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

# 后处理：集合转列表、处理空路径
# 转换集合为列表并处理类型序列化
for path in list(data_pattern.keys()):
    # 处理根路径的特殊情况
    if path == 'root':
        data_pattern[path]['type'] = type(
            None).__name__ if data is None else type(data).__name__

    # 转换类型对象为类型名称
    entry = data_pattern[path]
    if isinstance(entry['type'], type):
        if entry['type'] is type(None):
            entry['type'] = 'null'  # 或 'NoneType'
        else:
            entry['type'] = entry['type'].__name__

    # 转换集合为列表
    if 'possible_values' in entry:
        entry['possible_values'] = list(entry['possible_values'])

# create output folder if not exists
if not os.path.exists('output'):
    os.makedirs('output')

# Save data pattern into a prettified JSON file
with open('output/data_pattern.json', 'w', encoding='utf-8') as f:
    json.dump(data_pattern, f, ensure_ascii=False, indent=4)
