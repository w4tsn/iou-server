from fastapi import FastAPI

from iou.api.router import api_router

app = FastAPI(title='IOU')

app.include_router(api_router, prefix='/api')

@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'IOU as in I o(we) (yo)u'}