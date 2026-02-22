# Luminova Backend

This is the backend for the Luminova application. It is a FastAPI application with a modular structure, separating different applications and core functionalities.

## Project Structure

```
/luminova_backend/
├───.gitignore
├───alembic.ini
├───docker-compose.yml
├───Dockerfile
├───LICENSE
├───pyproject.toml
├───README.md
├───requirements.txt
├───server.conf
├───uv.lock
├───.git/...
├───.venv/...
└───app/
    ├───__init__.py
    ├───backend_pre_start.py
    ├───crud.py
    ├───initial_data.py
    ├───__pycache__/...
    ├───alembic/
    │   ├───env.py
    │   ├───README
    │   ├───script.py.mako
    │   ├───__pycache__/...
    │   └───versions/
    │       ├───.keep
    │       ├───ab245f407983_initial_migration.py
    │       └───__pycache__/...
    ├───core/
    │   ├───__init__.py
    │   ├───asgi.py
    │   ├───config.py
    │   ├───db.py
    │   ├───security.py
    │   ├───sso.py
    │   └───__pycache__/...
    ├───mainapps/
    │   ├───accounts/
    │   │   ├───__init__.py
    │   │   ├───models.py
    │   │   ├───utils.py
    │   │   ├───__pycache__/...
    │   │   └───api/
    │   │       ├───__init__.py
    │   │       ├───deps.py
    │   │       ├───urls.py
    │   │       ├───__pycache__/...
    │   │       └───views/
    │   │           ├───__init__.py
    │   │           ├───items.py
    │   │           ├───login.py
    │   │           ├───private.py
    │   │           ├───sso.py
    │   │           ├───users.py
    │   │           ├───utils.py
    │   │           └───__pycache__/...
    │   └───exams/
    └───templates/
        ├───build/...
        └───src/
            ├───new_account.mjml
            ├───reset_password.mjml
            └───test_email.mjml
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Create a `.env` file from the `.env.example` file and fill in the required environment variables.

3. Run the application using Docker Compose:

   ```bash
   docker-compose up -d
   ```

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file:

- `DOCKER_IMAGE_BACKEND`: The name of the backend Docker image.
- `DOCKER_IMAGE_FRONTEND`: The name of the frontend Docker image.
- `STACK_NAME`: The name of the docker-compose project.
- `DOMAIN`: The domain for the proxy.
- `ENVIRONMENT`: The environment.
- `SENTRY_DSN`: The Sentry DSN.
- `POSTGRES_SERVER`: The database host.
- `POSTGRES_USER`: The database user.
- `POSTGRES_PASSWORD`: The database password.
- `POSTGRES_DB`: The database name.
- `POSTGRES_PORT`: The database port.
- `SECRET_KEY`: The secret key for signing cookies and other things.
- `FIRST_SUPERUSER`: The first superuser.
- `FIRST_SUPERUSER_PASSWORD`: The first superuser password.
- `FIRST_SUPERUSER_FIRST_NAME`: The first superuser first name.
- `FIRST_SUPERUSER_LAST_NAME`: The first superuser last name.
- `SMTP_HOST`: The SMTP host.
- `SMTP_USER`: The SMTP user.
- `SMTP_PASSWORD`: The SMTP password.
- `EMAILS_FROM_EMAIL`: The email address to send emails from.
- `SMTP_TLS`: Whether to use TLS for SMTP.
- `SMTP_SSL`: Whether to use SSL for SMTP.
- `SMTP_PORT`: The SMTP port.
- `BACKEND_CORS_ORIGINS`: The CORS origins.
- `PROJECT_NAME`: The project name.
- `FRONTEND_HOST`: The frontend host.
- `GOOGLE_CLIENT_ID`: The Google client ID for SSO.
- `GOOGLE_CLIENT_SECRET`: The Google client secret for SSO.
- `MICROSOFT_CLIENT_ID`: The Microsoft client ID for SSO.
- `MICROSOFT_CLIENT_SECRET`: The Microsoft client secret for SSO.
- `LINKEDIN_CLIENT_ID`: The Linkedin client ID for SSO.
- `LINKEDIN_CLIENT_SECRET`: The Linkedin client secret for SSO.

## Running the Application

To run the application, you can use the following command:

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`.


## API Documentation

The API documentation is available at `http://localhost:8000/docs`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
