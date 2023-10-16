from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_NAME_TEST: str
    DB_USER_TEST: str
    DB_PASS_TEST: str

    @property
    def database_url_asyncpg(self):
        '''Асинхронная'''
        return (
            f'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'
        )

    @property
    def database_url_psycopg(self):
        '''Синхронная'''
        return (
            f'postgresql+psycopg://'
            f'{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'
        )
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
