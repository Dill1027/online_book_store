# gateway/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
from typing import Any

app = FastAPI(title="API Gateway", version="1.0.0")

# Service URLs
SERVICES = {
    "book": "http://localhost:3001"   # your Book Service port
}


async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    """Forward request to the appropriate microservice"""

    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            return JSONResponse(
                content=response.json() if response.text else None,
                status_code=response.status_code
            )

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }


# 📖 Book Service Routes

@app.get("/gateway/books")
async def get_all_books():
    """Get all books through gateway"""
    return await forward_request("book", "/api/books", "GET")


@app.get("/gateway/books/{book_id}")
async def get_book(book_id: int):
    """Get a book by ID through gateway"""
    return await forward_request("book", f"/api/books/{book_id}", "GET")


@app.post("/gateway/books")
async def create_book(request: Request):
    """Create a new book through gateway"""
    body = await request.json()
    return await forward_request("book", "/api/books", "POST", json=body)


@app.put("/gateway/books/{book_id}")
async def update_book(book_id: int, request: Request):
    """Update a book through gateway"""
    body = await request.json()
    return await forward_request("book", f"/api/books/{book_id}", "PUT", json=body)


@app.delete("/gateway/books/{book_id}")
async def delete_book(book_id: int):
    """Delete a book through gateway"""
    return await forward_request("book", f"/api/books/{book_id}", "DELETE")