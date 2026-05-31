from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    # 项目名称
    PROJECT_NAME: str = ""

    # 服务端口
    SERVER_PORT: int = 8082
    FRONTEND_PORT: int = 8081

    # 上下文记忆轮数
    CONTEXT_ROUNDS: int = 5

    # 工具调用最大轮数
    TOOL_CALL_MAX_ROUNDS: int = 5

    # MySQL
    MYSQL_HOST: str = ""
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""

    # 日志开关
    LOG_LLM: bool = True

    # Ark LLM
    ARK_API_KEY: str = Field(default="", alias="api_key")
    ARK_MODEL: str = Field(default="", alias="model")
    ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"

    @model_validator(mode="after")
    def _validate_not_empty(self):
        for field_name in ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_DATABASE"):
            if getattr(self, field_name) == "" or getattr(self, field_name) is None:
                raise ValueError(f"{field_name} 不能为空，请在 .env 中配置")
        return self

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


settings = Settings()
