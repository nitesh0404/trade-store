from fastapi import FastAPI


app = FastAPI(title="Trade Store API")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
