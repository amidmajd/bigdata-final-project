from fastapi import FastAPI

from .routes import router


BASE_URL = "/api/v1"

app = FastAPI(
    debug=True, title="Kafka API", openapi_url="/openapi.json", redoc_url=None, docs_url="/docs"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(router=router, prefix=f"{BASE_URL}/trip")
