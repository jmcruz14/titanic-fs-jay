from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse, RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .api_utils import limiter

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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(router)

@app.get('/health', tags=['system'])
@limiter.limit("5/minute")
async def root(request: Request):
  return {
    'status': 'OK'
  }

@app.exception_handler(429)
async def rate_limit_exceeded(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )
