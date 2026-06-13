from fastapi import FastAPI
import uvicorn
import controller
from service import profanityService

app = FastAPI()


@app.get('/health')
async def health():
    return {
        'status': 'ok',
        'modelLoaded': profanityService.isModelLoaded()
    }

if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8001, reload=True)

app.include_router(controller.router)
