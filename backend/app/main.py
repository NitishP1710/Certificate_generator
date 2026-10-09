from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.certificates import router as certificate_router
from app.api.routes.generation import router as generation_router
from app.api.routes.templates import router as template_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator", version="1.0.0")

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


app.include_router(template_router, prefix="/api")
app.include_router(generation_router, prefix="/api")
app.include_router(certificate_router, prefix="/api")
