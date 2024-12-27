# Secure File Sharing Application

A secure file-sharing web application built with React and Django REST Framework, featuring end-to-end encryption and multi-factor authentication.

## Features

- User Authentication with MFA support
- End-to-end file encryption
- Secure file sharing with access control
- Rule-based access control (RBAC)
- Shareable links with expiration

## Tech Stack

### Frontend
- React
- Redux for state management
- Tailwind CSS
- shadcn/ui components

### Backend
- Django REST Framework
- uv package manager
- SQLite (Development) / PostgreSQL (Production)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. Clone the repository
```bash
git clone [repository-url]
cd secure-file-share
```

2. Start the application using Docker Compose
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Security Features

- End-to-end encryption using AES-256
- Multi-factor authentication (TOTP)
- JWT-based authentication with secure cookie storage
- Rate limiting on sensitive endpoints
- Content Security Policy (CSP) headers
- CSRF protection
- Input validation and sanitization

## License

[License Type] - See LICENSE file for details 