from pathlib import Path
import uvicorn
from fastapi import FastAPI
from app.api.routers import main_router
from app.admin.admin import admin

BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / '.env'

app = FastAPI(title='mobile_app')

app.include_router(main_router)

admin.mount_to(app)


if __name__ == '__main__':

    uvicorn.run('main:app', reload=True, env_file=env_path)
