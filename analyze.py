import os
import json
from numbers import Number
from collections import defaultdict


def analyze_json_schema():
    # List to collect all JSON file paths 🚀
    json_file_list = []

    # Traverse the "data" directory and collect paths for all JSON files
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.json'):
                json_file_list.append(os.path.join(root, file))

    # Dictionary to store schema statistics for each JSON field path
    data_pattern = defaultdict(list)

    def create_entry(value):
        """
        Create a new statistical entry for the given value.
        The structure varies by data type.
        """
        if isinstance(value, bool):
            return {
                'type': bool,
                'count': 0,
                'possible_values': set()
            }
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            return {
                'type': type(value),
                'count': 0,
                'max_value': value,
                'min_value': value,
                'zero_count': 1 if value == 0 else 0,
                'positive_count': 1 if value > 0 else 0,
                'negative_count': 1 if value < 0 else 0
            }
        elif isinstance(value, str):
            return {
                'type': str,
                'count': 0,
                'max_length': len(value),
                'min_length': len(value),
                'possible_values': {value},
                'empty_count': 1 if value == "" else 0
            }
        elif isinstance(value, (list, dict)):
            return {
                'type': list if isinstance(value, list) else dict,
                'count': 0,
                'max_length': len(value),
                'min_length': len(value),
                'empty_count': 1 if len(value) == 0 else 0
            }
        elif value is None:
            return {
                'type': 'null',
                'count': 0,
                'possible_values': {None}
            }

    def upgrade_entry(int_entry, float_value):
        """
        Upgrade an existing integer entry to a float entry when a float value is encountered.
        This avoids maintaining separate entries for int and float.
        """
        upgraded = {
            'type': float,
            'count': int_entry['count'],  # carry over count without extra increment
            'max_value': float(int_entry['max_value']),
            'min_value': float(int_entry['min_value']),
            'zero_count': int_entry.get('zero_count', 0),
            'positive_count': int_entry.get('positive_count', 0),
            'negative_count': int_entry.get('negative_count', 0)
        }
        # Update statistics with the new float value
        upgraded['max_value'] = max(upgraded['max_value'], float_value)
        upgraded['min_value'] = min(upgraded['min_value'], float_value)
        if float_value == 0:
            upgraded['zero_count'] += 1
        elif float_value > 0:
            upgraded['positive_count'] += 1
        else:
            upgraded['negative_count'] += 1

        return upgraded

    def update_numeric_entry(entry, value):
        """
        Update a numeric (int or float) entry with a new value.
        This function updates the min, max, and count details without re‑incrementing the overall count.
        """
        entry['max_value'] = max(entry['max_value'], value)
        entry['min_value'] = min(entry['min_value'], value)

        if value == 0:
            entry['zero_count'] += 1
        elif value > 0:
            entry['positive_count'] += 1
        else:
            entry['negative_count'] += 1

    def analyze_value(value, path):
        """
        Recursively analyze the value and update statistics for the JSON path.
        """
        # Determine the current value type
        current_type = type(value) if value is not None else type(None)
        entries = data_pattern[path]

        # Handle numeric type conversion (upgrade int to float if needed)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            # Check for existing int or float entry for the field
            int_entry = next((e for e in entries if e['type'] is int), None)
            float_entry = next((e for e in entries if e['type'] is float), None)
            if isinstance(value, float) and int_entry:
                # Upgrade the int entry when a float value is encountered 🌟
                upgraded = upgrade_entry(int_entry, value)
                entries.remove(int_entry)

                if float_entry:
                    # Merge the upgraded statistics into the existing float entry
                    float_entry['count'] += upgraded['count']
                    float_entry['max_value'] = max(float_entry['max_value'], upgraded['max_value'])
                    float_entry['min_value'] = min(float_entry['min_value'], upgraded['min_value'])
                    float_entry['zero_count'] += upgraded['zero_count']
                    float_entry['positive_count'] += upgraded['positive_count']
                    float_entry['negative_count'] += upgraded['negative_count']
                else:
                    entries.append(upgraded)

                # Set the current type to float and ensure the value is float
                current_type = float
                value = float(value)

        # Find or create an entry for the current type
        entry = next((e for e in entries if e['type'] == current_type or
                      (current_type is type(None) and e['type'] == 'null')), None)
        if not entry:
            entry = create_entry(value)
            entries.append(entry)

        # Increment the overall count for this entry
        entry['count'] += 1

        # Explicitly handle boolean values first (to avoid treating them as numbers)
        if isinstance(value, bool):
            if 'possible_values' in entry and len(entry['possible_values']) < 10:
                entry['possible_values'].add(value)
        # Then handle numeric types (excluding booleans)
        elif isinstance(value, (int, float)):
            update_numeric_entry(entry, value)
        elif isinstance(value, str):
            entry['max_length'] = max(entry.get('max_length', 0), len(value))
            entry['min_length'] = min(entry.get('min_length', float('inf')), len(value))
            if 'empty_count' in entry:
                entry['empty_count'] += 1 if value == "" else 0
            if 'possible_values' in entry and len(entry['possible_values']) < 10:
                entry['possible_values'].add(value)
        elif isinstance(value, (list, dict)):
            coll_len = len(value)
            entry['max_length'] = max(entry.get('max_length', 0), coll_len)
            entry['min_length'] = min(entry.get('min_length', float('inf')), coll_len)
            if 'empty_count' in entry:
                entry['empty_count'] += 1 if coll_len == 0 else 0

        # Recursively analyze nested structures if applicable
        if isinstance(value, dict):
            for k, v in value.items():
                new_path = f"{path}.{k}" if path else k
                analyze_value(v, new_path)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                # Use ".[]" notation for list items (indexes are not distinguished here)
                new_path = f"{path}.[]" if path else ".[]"
                analyze_value(item, new_path)

    # Process each JSON file
    for json_file in json_file_list:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            analyze_value(data, 'root')

    # Post-process collected data for cleaner output
    for path in data_pattern:
        for entry in data_pattern[path]:
            # Convert type information to string names
            if entry['type'] is type(None) or entry['type'] == 'null':
                entry['type'] = 'null'
            else:
                entry['type'] = entry['type'].__name__

            # Round numeric values to two decimal places
            if entry['type'] in ('int', 'float'):
                for key in ['max_value', 'min_value']:
                    if isinstance(entry.get(key), float):
                        entry[key] = round(entry[key], 2)

            # Convert possible_values set to a list (limit to 10 items)
            if 'possible_values' in entry:
                entry['possible_values'] = list(entry['possible_values'])[:10]

    # Ensure output directory exists, then save the results to JSON
    if not os.path.exists('output'):
        os.makedirs('output')
    with open('output/data_pattern_final.json', 'w', encoding='utf-8') as f:
        json.dump(data_pattern, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    analyze_json_schema()
