from pydantic_settings import BaseSettings , SettingsConfigDict

class ArticlesSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" ,  extra="ignore")

    DATABASE_URL: str
    QIITA_ACCESS_TOKEN: str | None = None

settings = ArticlesSettings()

if __name__ == "__main__":
    print(settings.DATABASE_URL)


