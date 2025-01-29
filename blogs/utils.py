import re

def validate_password(password):
    # Regex pattern for validation: at least 8 characters, one uppercase letter, one lowercase letter, one digit, and one special character
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password)