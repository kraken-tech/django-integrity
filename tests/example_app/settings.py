from environs import Env


env = Env()


DATABASES = {
    "default": env.dj_db_url(
        "DATABASE_URL", default="postgres://localhost/django_integrity"
    ),
}
SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "tests.example_app",
]
USE_TZ = True
