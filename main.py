from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi_admin.factory import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from tortoise import fields, models
import os


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    password = fields.CharField(max_length=128)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await admin_app.configure(
        admin_secret="your-secret-key",
        providers=[UsernamePasswordProvider(User, "username", "password")],
    )
    admin_app.mount_to(app)


register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL"),
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
