from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from .api import router

app = FastAPI(
  title="TitanicAPI",
  version="0.1.0"
)

origins = [
  '*'
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

@app.get('/health', tags=['system'])
async def root(request: Request):
  return {
    'status': 'OK'
  }

app.include_router(router)