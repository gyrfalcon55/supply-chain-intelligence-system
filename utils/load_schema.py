import json


def get_schema():
    with open('schema.json') as file:
        schema = json.load(file)

        return schema
    

def get_relevant_schema(question, metadata, top_k=3):

    question = question.lower()

    scores = []

    for schema_name, tables in metadata.items():

        for table_name, table_info in tables.items():

            score = 0

            # Match keywords
            for keyword in table_info.get("keywords", []):

                keyword = keyword.lower()

                if keyword in question:
                    score += 2

            # Match table name
            if table_name.lower() in question:
                score += 5

            # Match schema name
            if schema_name.lower() in question:
                score += 3

            scores.append({
                "schema": schema_name,
                "table": table_name,
                "columns": table_info.get("columns", []),
                "description": table_info.get("description", ""),
                "score": score
            })

    scores.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    matched = [item for item in scores if item["score"] > 0]

    # If no matches, return top tables with full schema info
    if not matched:
        return scores[:top_k]

    return matched[:top_k]
