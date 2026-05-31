from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 项目名称
    PROJECT_NAME: str = "Chat Demo"

    # 服务端口
    SERVER_PORT: int = 8082
    FRONTEND_PORT: int = 8081

    # 上下文记忆轮数
    CONTEXT_ROUNDS: int = 5

    # 工具调用最大轮数
    TOOL_CALL_MAX_ROUNDS: int = 5

    # MySQL
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "data_agent"

    # Ark LLM
    ARK_API_KEY: str = Field(default="", alias="api_key")
    ARK_MODEL: str = Field(default="", alias="model")
    ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


settings = Settings()
