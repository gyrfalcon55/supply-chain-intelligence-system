from pathlib import Path

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

from configs.paths import COLANG_CONTENT_PATH, NEMO_CONFIG_PATH


class NeMoGuardrailsService:

    def __init__(self):
        self.config = self._load_config()
        self.guardrails = RunnableRails(self.config)

    def _load_config(self):
        colang_content = Path(
            COLANG_CONTENT_PATH
        ).read_text(encoding="utf-8")

        yaml_content = Path(
            NEMO_CONFIG_PATH
        ).read_text(encoding="utf-8")

        return RailsConfig.from_content(
            colang_content=colang_content,
            yaml_content=yaml_content,
        )

    def get_guardrails(self) -> RunnableRails:
        return self.guardrails