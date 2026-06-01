from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 项目名称
    PROJECT_NAME: str

    # 服务端口（前端默认8081，后端默认8082）
    SERVER_PORT: int = 8082
    FRONTEND_PORT: int = 8081

    # 上下文记忆轮数（默认5轮）
    CONTEXT_ROUNDS: int = 5

    # 工具调用最大轮数（默认5轮）
    TOOL_CALL_MAX_ROUNDS: int = 5

    # MySQL
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # 日志开关（默认关闭）
    LOG_LLM: bool = False

    # Ark LLM
    ARK_API_KEY: str
    ARK_MODEL: str
    ARK_BASE_URL: str

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


settings = Settings()
