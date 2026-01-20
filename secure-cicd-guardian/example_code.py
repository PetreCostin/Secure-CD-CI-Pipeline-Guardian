# Example Python project with security issues (FOR TESTING ONLY)

# SECRET: Hardcoded password
db_password = "super_secret_password_12345"

# SECRET: AWS Key
aws_access_key = "AKIAIOSFODNN7EXAMPLE"

# SAFE: Environment variable
import os
api_key = os.getenv("API_KEY")

class DatabaseConfig:
    # Vulnerable dependency would go here
    pass
