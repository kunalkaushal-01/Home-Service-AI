from fastapi import FastAPI
from routers import product_trained
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://3.139.209.129:3000","http://3.139.209.129"],  # or ["http://192.168.1.xxx:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(product_trained.router)
