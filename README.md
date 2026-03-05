# Event Management System - POS College Project

##  Project Overview

A comprehensive microservices-based event management platform developed for the POS (Programare Orientată pe Servicii) course at Universitatea Tehnică "Gheorghe Asachi" Iași. The system enables users to manage events, packages, and ticket bookings across multiple interconnected services.

##  Architecture

The project is built using a **microservices architecture** with the following components:

### Services

1. **IDM Service (Identity & Access Management)**
   - gRPC-based authentication server
   - User registration and login with JWT tokens
   - Role-based access control (admin, event-owner, client)
   - MariaDB database for user storage

2. **Event Manager API**
   - FastAPI REST API for managing events, packages, and tickets
   - MariaDB database backend
   - Features:
     - Create, read, update, delete events
     - Manage event packages with pricing
     - Ticket allocation and management
     - Secured endpoints with JWT authentication

3. **Client Manager API**
   - FastAPI REST API for client profile and ticket management
   - MongoDB database for flexible data storage
   - Features:
     - Client registration and profile management
     - Ticket purchase and booking history
     - Integrated with Event Manager service
     - gRPC authentication validation

4. **Frontend**
   - React + Vite single-page application
   - Real-time responsive UI
   - Features:
     - User authentication and login
     - Event listing and browsing
     - Event registration and booking
     - User profile management
     - Attendees tracking



##  Project Structure

```
.
├── idm-service/              # Identity Management Service (gRPC)
│   ├── server.py             # gRPC authentication server
│   ├── auth_db.py            # Database models for users
│   ├── auth.proto            # Protocol Buffer definitions
│   └── create_users.py       # User seeding script
│
├── event-manager/            # Event Management API (FastAPI)
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic request/response models
│   ├── dependencies.py       # Authentication dependencies
│   └── db/
│       ├── database.py       # Database connection setup
│       ├── models_db.py      # SQLAlchemy ORM models
│       └── crud.py           # Database CRUD operations
│
├── client-manager/           # Client Management API (FastAPI)
│   ├── main_client.py        # FastAPI application
│   ├── models_client.py      # Pydantic models
│   ├── db_mongo.py           # MongoDB connection
│   ├── dependencies.py       # Authentication & validation
│   └── .env                  # Environment configuration
│
├── frontend/                 # React Vite Application
│   ├── src/
│   │   ├── pages/            # Page components (Login, Events, Profile)
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React Context API (AuthContext)
│   │   ├── services/         # API client services
│   │   └── App.jsx           # Main application component
│   └── package.json          # Dependencies
│
└── docker-compose.yml        # Multi-container configuration
```

##  Features Implemented

### Authentication & Authorization
-  User registration with role-based assignment
-  JWT-based authentication using gRPC
-  Token validation across all services
-  Secure password hashing

### Event Management
-  Create and manage events
-  Package creation with flexible pricing
-  Ticket allocation per package
-  Event filtering and search
-  Event attendees tracking

### Client Management
-  User profile management
-  Ticket booking and history
-  MongoDB integration for flexible data storage

### Frontend
-  Responsive authentication interface
-  Event discovery and browsing
-  Event registration flow
-  User profile and booking management
-  Navigation with React Router

##  Inter-Service Communication

- **gRPC**: IDM Service ↔ Event Manager / Client Manager (for authentication)
- **HTTP/REST**: Frontend ↔ Event Manager & Client Manager APIs
- **Database**: Service-specific (MariaDB for events, MongoDB for clients)

##  Key Implementation Details

- **Containerized Deployment**: All services run in Docker containers orchestrated by Docker Compose
- **CORS Support**: Frontend integration with backend services
- **Error Handling**: Comprehensive HTTP status codes and error messages
- **Environment Configuration**: `.env` files for service configuration
- **Database Migrations**: Automatic table creation on service startup

