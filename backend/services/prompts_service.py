from configs.config import load_config
from configs.paths import ANALYTICS_FORMAT_OUPUT_PROMPT_PATH, ANALYTICS_GENERATE_SQL_PROMPT_PATH

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

ANALYTICS_GENERATE_SQL_PROMPT = load_prompt(
    ANALYTICS_GENERATE_SQL_PROMPT_PATH
)

ANALYTICS_FORMAT_OUTPUT_PROMPT = load_prompt(
    ANALYTICS_FORMAT_OUPUT_PROMPT_PATH
)


