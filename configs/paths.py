from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

CONFIG_PATH = BASE_DIR / "configs" / "config.yml"


PROMPTS_PATH = BASE_DIR / "backend" / "agents" / "analytics_agent" / "prompts"


ANALYTICS_FORMAT_OUPUT_PROMPT_PATH = PROMPTS_PATH / "analytics_format_output.txt"

ANALYTICS_GENERATE_SQL_PROMPT_PATH = PROMPTS_PATH / "analytics_generate_sql.txt"


ANALYTIC_DB_SCHEMAS_PATH = BASE_DIR / "backend" / "schemas" / "analytics_schema.json"