import os
import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

SONARQUBE_URL = os.getenv("SONARQUBE_URL", "http://localhost:9000")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "127.0.0.1")

app = FastAPI(
    title="Code Fixer Agent",
    version="1.0.0",
    description="AI-powered code fixing agent integrated with SonarQube",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_sonarqube_connection() -> bool:
    """
    Check if SonarQube is running and accessible.

    Returns:
        bool: True if SonarQube is accessible, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SONARQUBE_URL}/api/system/status")

            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                logger.info(
                    f"SonarQube is running - Status: {status}",
                    origin="startup_event",
                    data={"url": SONARQUBE_URL, "status": status},
                )
                return True

            logger.error(
                f"SonarQube returned unexpected status code: {response.status_code}",
                origin="startup_event",
            )
            return False

    except httpx.ConnectError:
        logger.error(
            f"Failed to connect to SonarQube at {SONARQUBE_URL}",
            origin="startup_event",
            data={"error": "Connection refused - Is SonarQube running?"},
        )
        return False

    except httpx.TimeoutException:
        logger.error(
            f"Timeout connecting to SonarQube at {SONARQUBE_URL}",
            origin="startup_event",
        )
        return False

    except Exception as e:
        logger.error(
            f"Unexpected error checking SonarQube: {str(e)}",
            origin="startup_event",
            data={"error": str(e)},
        )
        return False


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting application...", origin="startup_event")

    sonarqube_running = await check_sonarqube_connection()

    if not sonarqube_running:
        error_msg = (
            f"CRITICAL: SonarQube is not running or not accessible at {SONARQUBE_URL}. "
            "Please start SonarQube before running this application."
        )
        logger.error(error_msg, origin="startup_event")
        raise RuntimeError(error_msg)

    logger.info("Application startup completed successfully", origin="startup_event")


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict:
    logger.info("Health check", origin="health_check")
    return {
        "status": "OK",
        "service": "Code Fixer Agent",
        "sonarqube_url": SONARQUBE_URL,
    }


if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}", origin="main")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
