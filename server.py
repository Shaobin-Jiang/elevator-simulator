from contextlib import asynccontextmanager
import os
import webbrowser

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_BACKEND_URL = "http://127.0.0.1:8000"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register client on startup (same behavior as original script)
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BASE_BACKEND_URL}/api/client/register",
                headers={"Content-Type": "application/json", "X-Client-Type": "gui"},
            )
    except Exception:
        # Ignore registration failures to not block app startup
        pass

    # Open the browser to the demo page
    try:
        webbrowser.open("http://127.0.0.1:5137/demo/index.html")
    except Exception:
        pass

    yield


app = FastAPI(lifespan=lifespan)

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/demo", StaticFiles(directory=templates_dir), name="demo")


@app.get("/proxy")
async def proxy(
    request_type: str = Query("", alias="type"),
    tick: int = Query(0),
):
    try:
        async with httpx.AsyncClient() as client:
            if request_type == "state":
                resp = await client.get(f"{BASE_BACKEND_URL}/api/state")
                resp.raise_for_status()
                return JSONResponse(resp.json())

            if request_type == "step":
                payload = {"current_tick": tick, "ticks": 1}
                resp = await client.post(
                    f"{BASE_BACKEND_URL}/api/step",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                return JSONResponse(resp.json())

            return JSONResponse({"message": "Nothing"})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5137, reload=False)
