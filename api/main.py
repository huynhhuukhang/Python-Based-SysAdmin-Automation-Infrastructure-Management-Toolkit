import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from sysadmin_toolkit.api.database import init_database
from sysadmin_toolkit.api.routes.agent import router as agent_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    logging.info("SysAdmin API started")

    yield

    logging.info("SysAdmin API stopped")


app = FastAPI(
    title="SysAdmin Automation Toolkit",
    description="Central monitoring and infrastructure management API",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(agent_router)


@app.get("/")
def root():
    return {
        "name": "SysAdmin Automation Toolkit",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }