# Service Startup Guide

## Port Configuration
- **Book Service**: 8001
- **Cart Service**: 8002
- **Customer Service**: 8003
- **Order Service**: 8004
- **API Gateway**: 8000

## Startup Commands

### Terminal 1: Gateway (Port 8000)
```powershell
Set-Location "D:\SLIIT\Y4S1\MTIT\Assigment 2\book-online-store-fastapi\gateway"
uvicorn main:app --reload --port 8000
```

### Terminal 2: Book Service (Port 8001)
```powershell
Set-Location "D:\SLIIT\Y4S1\MTIT\Assigment 2\book-online-store-fastapi\book-service"
uvicorn main:app --reload --port 8001
```

### Terminal 3: Cart Service (Port 8002)
```powershell
Set-Location "D:\SLIIT\Y4S1\MTIT\Assigment 2\book-online-store-fastapi\cart-service"
uvicorn main:app --reload --port 8002
```

### Terminal 4: Customer Service (Port 8003)
```powershell
Set-Location "D:\SLIIT\Y4S1\MTIT\Assigment 2\book-online-store-fastapi\customer-service"
uvicorn main:app --reload --port 8003
```

### Terminal 5: Order Service (Port 8004)
```powershell
Set-Location "D:\SLIIT\Y4S1\MTIT\Assigment 2\book-online-store-fastapi\order-service"
uvicorn main:app --reload --port 8004
```

## Access Points
- **API Gateway**: http://127.0.0.1:8000
- **Books API**: http://127.0.0.1:8001
- **Cart API**: http://127.0.0.1:8002
- **Customers API**: http://127.0.0.1:8003
- **Orders API**: http://127.0.0.1:8004

## Gateway Routing
The gateway on port 8000 automatically routes requests to the correct services:
- `/api/books/*` → Book Service (8001)
- `/api/cart/*` → Cart Service (8002)
- `/api/customers/*` → Customer Service (8003)
- `/api/orders/*` → Order Service (8004)
