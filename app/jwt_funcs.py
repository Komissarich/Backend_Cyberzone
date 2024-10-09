from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt
import os

ACCESS_TOKEN_EXPIRE_MINUTES = 10
ALGORITHM = "HS256"
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(
    data,
):
    to_encode = data.copy()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def jwt_check(header, connection):
    cursor = connection.cursor()
    try:

        jwt_token = header.split()[1]
        decoded = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (decoded["username"],)
        )
        result = cursor.fetchall()
        if result[0][2] != decoded["hashed_password"]:
            return False
        return decoded

    except BaseException:
        return False
