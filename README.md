# 📊 JSONStructAnalyzer

> A lightweight Python tool that recursively analyzes the structure of all JSON files in a directory and generates statistical summaries for each data field.

---

## 🔍 Features

- Recursive traversal of nested JSON objects and arrays  
- Automatic detection of:
  - Field types (e.g. `string`, `number`, `boolean`, `object`, `array`, `null`)
  - Field occurrence count
  - Value ranges (`min` / `max` for numbers)
  - Length ranges (`min_length` / `max_length` for strings, lists, objects)
  - Sample values (up to 10 for each field)

Perfect for:

- Data profiling and exploration  
- Schema inference  
- Cleaning messy JSON datasets  
- Preparing for database imports or validation

---

## 📂 Input

Place your `.json` files under a folder named `data/`. The script will recursively process all subdirectories and files.

---

## ⚙️ Usage

1. Clone the repository:

```bash
git clone https://github.com/Kingsmai/JSON-Struct-Analyzer.git
cd JSON-Struct-Analyzer
```

2. Add your JSON files under the `data/` directory.

```bash
mkdir data
# Add .json files here
```

3. Run the analyzer:

```bash
python analyze.py
```

The output will be printed as a Python dictionary named `data_pattern`, and save as JSON file at the `output` directory.

---

## 🧪 Example Output

```json
{
  "root.user.name": {
    "type": "str",
    "count": 120,
    "min_length": 2,
    "max_length": 12,
    "possible_values": ["Alice", "Bob", "Charlie"]
  },
  "root.user.age": {
    "type": "int",
    "count": 120,
    "min_value": 18,
    "max_value": 65
  }
}
```

---

## 📦 Requirements

- Python 3.7+
- No third-party libraries required (uses only the standard library)

---

## 🚀 Roadmap Ideas

This tool can be extended to support:

- JSON schema generation
- Integration with data validation tools
- CLI interface and argument flags
- Web dashboard for visualization (e.g., Streamlit)

---

## 🛠️ Contributing

Contributions are welcome! Feel free to fork, submit issues, or open a pull request.

---

## 📄 License

MIT License © 2025 Xiaomai
