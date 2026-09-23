import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-not-for-production")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/pytest_app.db")
