from pydantic_settings import BaseSettings , SettingsConfigDict

class ArticlesSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" ,  extra="ignore")

    DATABASE_URL:str

settings = ArticlesSettings()

print(settings.DATABASE_URL)


