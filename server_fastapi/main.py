from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config.database import connect_db, close_db
from config.settings import settings
from routes import auth, cases, judgments, ai, reminders, profile, admin, feedback

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="LexiBot API",
    description="AI-Powered Legal Research and Case Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = ["http://localhost:5173", "http://localhost:5174"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide better error messages"""
    errors = exc.errors()
    print(f"Validation error on {request.url}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )

# Health check route
@app.get("/")
async def root():
    return {"message": "LexiBot API is running..."}

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(admin.router)
app.include_router(ai.router)
app.include_router(cases.router)
app.include_router(judgments.router)
app.include_router(reminders.router)
app.include_router(feedback.router)

# Handle unknown routes
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path_name: str):
    return {"message": "Route not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
