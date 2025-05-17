import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_POLICY = {
    "min_length": 8,
    "uppercase": True,
    "lowercase": True,
    "digits": True,
    "special": True,
}

def validate_password(password: str) -> bool:
    if len(password) < PASSWORD_POLICY["min_length"]:
        return False
    if PASSWORD_POLICY["uppercase"] and not re.search(r"[A-Z]", password):
        return False
    if PASSWORD_POLICY["lowercase"] and not re.search(r"[a-z]", password):
        return False
    if PASSWORD_POLICY["digits"] and not re.search(r"\d", password):
        return False
    if PASSWORD_POLICY["special"] and not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
