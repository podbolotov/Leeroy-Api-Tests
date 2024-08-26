import hashlib
from data.framework_variables import FrameworkVariables as FrVars


def hash_password(password: str):
    salt = FrVars.PASSWORD_HASH_SALT

    password_prepared_for_hashing = password + salt
    hashed_password = hashlib.md5(password_prepared_for_hashing.encode())

    return hashed_password.hexdigest()
