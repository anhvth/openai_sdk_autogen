import argparse
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hello World API", version="1.0.0", openapi_version="3.0.3")


class HealthResponse(BaseModel):
    status: str
    service: str


class GreetingResponse(BaseModel):
    message: str
    user_name: str
    timestamp: str
    personalized: bool


class GreetingRequest(BaseModel):
    greeting_type: Union[str, None] = "hello"
    include_timestamp: Union[bool, None] = True


@app.get("/", operation_id="root_get")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}


@app.get("/health", operation_id="health_check")
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", service="hello-world-api")


@app.post("/greeting/{user_name}", operation_id="create_greeting")
async def create_greeting(user_name: str, request: GreetingRequest) -> GreetingResponse:
    """Create a personalized greeting for the user."""
    from datetime import datetime

    greeting_type = request.greeting_type or "hello"
    current_time = datetime.now().isoformat() if request.include_timestamp else ""

    message = f"{greeting_type.title()}, {user_name}!"

    return GreetingResponse(
        message=message, user_name=user_name, timestamp=current_time, personalized=True
    )


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the Hello World API server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to run the server on"
    )
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
