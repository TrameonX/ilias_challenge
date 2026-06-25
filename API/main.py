from fastapi import FastAPI
from API.controllers import router as ai_pipeline_router


app = FastAPI(title="AI File Processing Platform")

app.include_router(ai_pipeline_router)

@app.get("/")
def read_root():
    return {"message": "Le backend de la plateforme IA est opérationnel."}