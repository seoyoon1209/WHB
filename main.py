from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import dbpool
from router.AuthRouter import router as AuthRouter
from router.OnboardRouter import router as OnboardRouter
from router.RecordRouter import router as RecordRouter
from router.DiaryRouter import router as DiaryRouter
from router.PredictionRouter import router as PredictionRouter
from router.FeedbackRouter import router as FeedbackRouter
from router.HistoryRouter import router as HistoryRouter
from router.SettingRouter import router as SettingRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dbpool.init()
    print("DB connected")
    yield
    await dbpool.dispose()
    print("DB disconnected")


app = FastAPI(title="WH API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://wmf-j7ri.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter, prefix="/api")
app.include_router(OnboardRouter, prefix="/api")
app.include_router(RecordRouter, prefix="/api")
app.include_router(DiaryRouter, prefix="/api")
app.include_router(PredictionRouter, prefix="/api")
app.include_router(FeedbackRouter, prefix="/api")
app.include_router(HistoryRouter, prefix="/api")
app.include_router(SettingRouter, prefix="/api")


@app.get("/")
async def root():
    return {"message": "WH API"}
