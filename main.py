from fastapi import FastAPI, Request
import time


from src.routes import contacts


app = FastAPI()
app.include_router(contacts.router, prefix='/api')


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
def read_root():
    return {"message": "Hello World"}
