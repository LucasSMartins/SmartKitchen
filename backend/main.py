from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router

app = FastAPI(
    title='smartkitchen',
    version='0.1.0',
    description='APP perfeito para salva as suas receitas favoritas.'
)

app.include_router(api_router, prefix='/api')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", reload=True, log_level='info')
