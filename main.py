import uvicorn
from app.config import settings
from app.api import app

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 