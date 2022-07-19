from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api_routes import router

BASE_URL = "/api"

app = FastAPI(
    debug=True, title="Kafka API", openapi_url="/openapi.json", redoc_url=None, docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(router=router, prefix=f"{BASE_URL}/trip")
