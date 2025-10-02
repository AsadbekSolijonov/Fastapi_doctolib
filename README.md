# Doctolib API

A modern, production-ready FastAPI application for managing medical appointments, doctors, patients, and specialties. Built with SQLModel, Alembic, and JWT authentication.

## Features

- **Authentication & Authorization**
  - JWT-based authentication with access and refresh tokens
  - Token rotation and blacklisting for enhanced security
  - Role-based access control (Patient, Doctor, Admin)
  - Secure cookie-based refresh token storage

- **User Management**
  - User registration with role assignment
  - Profile management
  - Doctor specialty associations

- **Database**
  - SQLModel ORM for type-safe database operations
  - Alembic migrations for schema versioning
  - Support for SQLite (development) and PostgreSQL (production)

## Tech Stack

- **Framework**: FastAPI 0.116.2+
- **ORM**: SQLModel 0.0.25
- **Database Migrations**: Alembic 1.16.5+
- **Authentication**: python-jose (JWT), passlib (password hashing)
- **Configuration**: pydantic-settings
- **Package Manager**: uv

## Prerequisites

- Python 3.9+
- uv (recommended) or pip

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd fast-doctolib

# Install dependencies
make sync

# Or manually
uv sync
```

### Using pip

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./doctolib.db
# For PostgreSQL: postgresql+psycopg2://user:password@localhost:5432/doctolib

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_COOKIE_NAME=refresh_token
```

**Security Note**: Generate a secure SECRET_KEY using:
```bash
openssl rand -hex 32
```

## Database Setup

### Initialize Database

```bash
# Create initial migration
make alembic_rev MSG="initial setup"

# Apply migrations
make upgrade

# Or do both at once
make migrate MSG="initial setup"
```

### Migration Commands

```bash
# Create a new migration
make alembic_rev MSG="add new table"

# Apply migrations
make upgrade

# Rollback last migration
make downgrade

# View migration history
make history

# View current heads
make heads
```

## Running the Application

### Development Mode (with auto-reload)

```bash
make run_dev

# Or with custom host/port
make run_dev HOST=0.0.0.0 PORT=8080
```

### Production Mode

```bash
make run_prod

# Or with custom configuration
make run_prod HOST=0.0.0.0 PORT=8000 WORKERS=4
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once the server is running, access:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get tokens | No |
| POST | `/api/v1/auth/logout` | Logout and invalidate tokens | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes (Refresh Token) |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users/` | List all users | Yes |
| GET | `/api/v1/users/me` | Get current user profile | Yes |

## Request Examples

### Register a Patient

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register?role=patient" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "password": "SecurePass123",
    "bio": "Patient bio"
  }'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Access Protected Endpoint

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your-access-token>"
```

## Project Structure

```
fast-doctolib/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   ├── env.py             # Alembic environment
│   └── script.py.mako     # Migration template
├── app/
│   ├── api/
│   │   ├── endpoints/     # API route handlers
│   │   │   ├── auth.py   # Authentication endpoints
│   │   │   └── user.py   # User endpoints
│   │   ├── security_utils/ # Security utilities
│   │   │   ├── password.py # JWT & password handling
│   │   │   └── auth_state.py # Auth middleware
│   │   └── exceptions.py  # Custom exceptions
│   ├── core/
│   │   └── config.py      # Application configuration
│   ├── db/
│   │   └── session.py     # Database session management
│   ├── models/            # SQLModel database models
│   │   ├── user.py
│   │   └── specialty.py
│   ├── schema/            # Pydantic schemas (DTOs)
│   │   ├── auth.py
│   │   └── user.py
│   └── main.py            # Application entry point
├── .env                    # Environment variables (not in git)
├── .gitignore
├── alembic.ini            # Alembic configuration
├── Makefile               # Development commands
├── pyproject.toml         # Project dependencies
└── README.md
```

## Development

### Code Quality

```bash
# Format code
make fmt

# Lint code
make lint

# Clean cache files
make clean
```

### Adding New Models

1. Create model in `app/models/your_model.py`
2. Import in `app/models/__init__.py`
3. Create migration: `make alembic_rev MSG="add your_model"`
4. Apply migration: `make upgrade`

## Security Features

- **Password Hashing**: Bcrypt with automatic salt generation
- **JWT Tokens**: Secure token generation with JTI (JWT ID)
- **Token Blacklist**: In-memory token revocation (consider Redis for production)
- **Refresh Token Rotation**: New refresh token on each refresh to detect reuse
- **HTTP-Only Cookies**: Refresh tokens stored in secure cookies
- **CORS Protection**: Configure allowed origins for production

## Production Deployment

### Recommendations

1. **Environment Variables**
   - Use strong, randomly generated SECRET_KEY
   - Set `secure=True` for cookies in HTTPS environment
   - Configure DATABASE_URL for PostgreSQL

2. **Database**
   - Use PostgreSQL or MySQL instead of SQLite
   - Enable connection pooling
   - Set up database backups

3. **Token Storage**
   - Implement Redis for token blacklist
   - Configure appropriate token expiration times

4. **Security**
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Implement logging and monitoring

5. **Deployment**
   ```bash
   # Using Docker (example)
   docker build -t doctolib-api .
   docker run -p 8000:8000 --env-file .env doctolib-api
   ```

## Known Issues & Future Improvements

### Current Limitations

1. **Token Blacklist**: Currently uses in-memory storage (lost on restart)
   - **Solution**: Implement Redis-based blacklist for production

2. **Specialty Assignment**: Doctor registration doesn't validate specialty_id
   - **Fix included**: See bug fixes below

### Planned Features

- [ ] Appointment scheduling system
- [ ] Doctor availability management
- [ ] Email notifications
- [ ] Password reset functionality
- [ ] Admin dashboard
- [ ] API rate limiting
- [ ] Comprehensive test suite

## Bug Fixes Applied

Several critical bugs have been identified and fixed:

1. **Auth Registration**: Fixed specialty_id validation for doctors
2. **Token Refresh**: Improved token handling and error messages
3. **Database Session**: Fixed SQLite foreign key enforcement

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact: [your-email@example.com]

## Acknowledgments

- FastAPI framework and community
- SQLModel for the excellent ORM
- All contributors to this project