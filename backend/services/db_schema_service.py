import json

def load_schema(filepath: str) -> list:
    with open(filepath) as f:
        raw = json.load(f)

    flat = []
    for schema_name, tables in raw.items():
        for table_name, table_info in tables.items():
            flat.append({
                "schema": schema_name,
                "table": table_name,
                "description": table_info.get("description", ""),
                "keywords": table_info.get("keywords", []),
                "columns": list(table_info["columns"].keys())  # exact names, code-extracted
            })
    return flat