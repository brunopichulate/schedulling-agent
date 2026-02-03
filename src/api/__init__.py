from fastapi import FastAPI, Depends
from starlette.types import Lifespan

from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from src.api.common import common_router
from src.api.v1 import api_v1_router
from fastapi_limiter.depends import RateLimiter

def create_app(lifespan: Lifespan | None = None) -> FastAPI:
  """Create and configure the FastAPI application."""
  app = FastAPI(
    title="Endeavor Chatbot API",
    description="API do chatbot Endeavor",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/",
    dependencies=[
      # Add global dependencies here if needed
      Depends(RateLimiter(times=5, seconds=1))
    ],
  )
  # Enable CORS
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  # Include routers
  app.include_router(common_router)
  app.include_router(api_v1_router)

  RequestsInstrumentor().instrument()
  FastAPIInstrumentor.instrument_app(
    app, excluded_urls="/(|health|metrics|redoc|openapi.json).*"
  )

  return app
