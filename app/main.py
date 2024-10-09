from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from app.jwt_funcs import create_access_token, jwt_check
import os
import json
import re
import bcrypt
import psycopg2
import uuid

app = FastAPI(title="FastAPI, Docker, and Traefik")
load_dotenv()
postgres_database = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port = os.getenv("POSTGRES_PORT")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

salt = bcrypt.gensalt()


connection = psycopg2.connect(
    user=postgres_user,
    password=postgres_password,
    host=postgres_host,
    port=postgres_port,
    database=postgres_database,
)

connection.autocommit = True


@app.post("/api/auth/register")
def registration(request: Request, username: str, password: str):
    cursor = connection.cursor()

    data = request.query_params

    if len(data["username"]) < 4 or len(data["username"]) > 30:
        return JSONResponse(
            content={
                "message": "Wrong username length! Minimum length is 4 letters, maximum is 30"
            },
            status_code=400,
        )

    if password_check(data["password"]) is False:
        return JSONResponse(
            content={
                "message": "Password must contain a-z, at least one upper case letter A-Z, at least one digit, and a minimum length is 6, maximum is 100"
            },
            status_code=400,
        )
    pw_hash = bcrypt.hashpw(data["password"].encode("utf-8"), salt).decode("utf-8")
    cursor.execute(
        "SELECT * from users WHERE username = %s",
        (data["username"],),
    )
    res = cursor.fetchall()

    if len(res) > 0:
        return JSONResponse(
            content={"message": "User whith the same info is already exists"},
            status_code=409,
        )
    cursor.execute(
        "INSERT INTO users (username, password, created_at, updated_at) VALUES (%s, %s, %s, %s)",
        (
            data["username"],
            pw_hash,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        ),
    )
    return JSONResponse(
        content={
            "profile": dict(
                username=data["username"],
                created_at=str(datetime.now(timezone.utc) + timedelta(hours=3)),
                updated_at=str(datetime.now(timezone.utc) + timedelta(hours=3)),
            ),
        },
        status_code=200,
    )


@app.post("/api/auth/sign_in")
def sign_in(request: Request):
    cursor = connection.cursor()

    data = request.query_params
    cursor.execute("SELECT * from users WHERE username = %s", (data["username"],))
    res = cursor.fetchall()

    if len(res) > 0:
        hash_pw = res[0][2]

        if (
            bcrypt.checkpw(data["password"].encode("utf-8"), hash_pw.encode("utf-8"))
            is False
        ):

            return JSONResponse(
                content={"message": "Wrong username/password"}, status_code=401
            )
        else:
            token = create_access_token(
                {"username": data["username"], "hashed_password": res[0][2]}
            )

            return JSONResponse(content={"message": token}, status_code=200)
    else:
        return JSONResponse(
            content={"message": "Wrong username/password"}, status_code=401
        )


@app.get("/api/me")
def show_my_profile(request: Request):
    cursor = connection.cursor()
    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)
    cursor.execute(
        "SELECT * from users WHERE username = %s",
        (decoded["username"],),
    )
    res = cursor.fetchall()
    return JSONResponse(
        content={
            "profile": dict(
                username=decoded["username"],
                created_at=str(res[0][3]),
                updated_at=str(res[0][4]),
            ),
        },
        status_code=200,
    )


@app.patch("/api/me")
def update_password(request: Request):
    cursor = connection.cursor()
    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    data = request.query_params
    username = decoded["username"]
    if password_check(data["password"]) is False:
        return JSONResponse(
            content={
                "message": "Password must contain a-z, at least one upper case letter A-Z, at least one digit, and a minimum length is 6, maximum is 100"
            },
            status_code=400,
        )
    pw_hash = bcrypt.hashpw(data["password"].encode("utf-8"), salt).decode("utf-8")
    cursor.execute(
        f"UPDATE users SET password = '{pw_hash}', updated_at = '{str(datetime.now(timezone.utc) + timedelta(hours=3))}' WHERE username = '{username}'"
    )
    cursor.execute(
        "SELECT * from users WHERE username = %s",
        (username,),
    )
    res = cursor.fetchall()
    return JSONResponse(
        content={
            "profile": dict(
                username=username,
                created_at=str(res[0][3]),
                updated_at=str(res[0][4]),
            ),
        },
        status_code=200,
    )


@app.post("/api/posts/new")
def create_new_post(request: Request):
    cursor = connection.cursor()

    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    data = request.query_params
    if len(data["text"]) > 1000:
        return JSONResponse(
            content={"message": "Maximum length of content is 1000"}, status_code=400
        )
    uid = uuid.uuid1()
    cursor.execute(
        "INSERT INTO posts VALUES (%s, %s, %s, %s, %s)",
        (
            str(uid),
            data["text"],
            decoded["username"],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        ),
    )
    return JSONResponse(
        content={
            "created_post": dict(
                id=str(uid),
                text=data["text"],
                created_at=str(datetime.now(timezone.utc) + timedelta(hours=3)),
                updated_at=str(datetime.now(timezone.utc) + timedelta(hours=3)),
            ),
        },
        status_code=200,
    )


@app.patch("/api/posts/update_post")
def update_post(request: Request):
    cursor = connection.cursor()

    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    data = request.query_params
    cursor.execute(
        "SELECT * FROM posts WHERE id = %s AND user_id = %s",
        (data["post_id"], decoded["username"]),
    )
    res = cursor.fetchall()
    if len(res) == 0:
        return JSONResponse(content={"message": "Post not found"}, status_code=404)
    cursor.execute(
        "UPDATE posts SET text = %s, updated_at = %s WHERE id = %s AND user_id = %s",
        (
            data["text"],
            str(datetime.now(timezone.utc) + timedelta(hours=3)),
            data["post_id"],
            decoded["username"],
        ),
    )
    cursor.execute("SELECT * FROM posts WHERE id = %s", (data["post_id"],))
    result = cursor.fetchall()
    return JSONResponse(
        content={
            "updated_post": dict(
                id=result[0][0],
                text=result[0][1],
                user_id=result[0][2],
                created_at=str(result[0][3]),
                updated_at=str(result[0][4]),
            ),
        },
        status_code=200,
    )


@app.delete("/api/posts/delete_post")
def delete_post(request: Request):
    cursor = connection.cursor()
    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        cursor.close()
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    data = request.query_params
    cursor.execute(
        "SELECT * FROM posts WHERE id = %s AND user_id = %s",
        (data["post_id"], decoded["username"]),
    )
    res = cursor.fetchall()
    if len(res) == 0:
        cursor.close()
        return JSONResponse(content={"message": "Post not found"}, status_code=409)

    cursor.execute("DELETE FROM posts WHERE id = %s", (data["post_id"],))
    return JSONResponse(
        content={
            "Message": "Successfull deleting of post",
            "Your posts": show_posts(decoded["username"]),
        },
        status_code=200,
    )


# vlados asbdashj1212A / vladosVLAD123


@app.post("/api/posts")
def show_post_by_id(request: Request, postId: str = ""):
    cursor = connection.cursor()

    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        cursor.close()
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    cursor.execute("SELECT * FROM posts WHERE id=%s", (postId,))
    result = cursor.fetchall()

    if len(result) > 0:
        return JSONResponse(
            content={
                "Post": dict(
                    id=result[0][0],
                    text=result[0][1],
                    user_id=result[0][2],
                    created_at=str(result[0][3]),
                    updated_at=str(result[0][4]),
                ),
            },
            status_code=200,
        )
    else:
        return JSONResponse(
            content={"message": "Post with that id not found"}, status_code=404
        )


@app.post("/api/posts/user_posts")
def show_user_posts(request: Request, username: str = ""):
    cursor = connection.cursor()
    decoded = jwt_check(request.headers.get("Authorization"), connection)
    if decoded is False:
        cursor.close()
        return JSONResponse(content={"message": "Wrong token"}, status_code=409)

    cursor.execute("SELECT * FROM posts WHERE user_id = %s", (username,))
    result = cursor.fetchall()
    if len(result) == 0:
        return JSONResponse(content={"message": "User not found"}, status_code=404)
    cursor.close()
    return JSONResponse(content={"Posts": show_posts(username)}, status_code=200)


def password_check(password):
    if not (
        re.fullmatch(
            r"^(?=.*\d{1})(?=.*[a-z]{1})(?=.*[A-Z]{1})[a-zA-Z0-9]{6,24}$",
            password,
        )
        and len(password) >= 6
        and len(password) < 100
    ):
        return False
    else:
        return True


def show_posts(username):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM posts WHERE user_id = %s", (username,))
    result = cursor.fetchall()
    result.sort(key=lambda row: row[4])
    result = result[::-1]
    response = [
        dict(
            id=row[0],
            text=row[1],
            user_id=row[2],
            created_at=str(row[3]),
            update_at=str(row[4]),
        )
        for row in result
    ]

    cursor.close()
    return response
