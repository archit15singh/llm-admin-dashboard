from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from starlette_admin import Admin, ModelView, filters
from starlette_admin.contrib.tortoise import TortoiseAdmin
from tortoise import fields, models
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class UserQuestion(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    question = fields.TextField()
    answer = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)


class TimestampFilter(filters.BaseFilter):
    def __init__(self, name: str, interval: timedelta):
        super().__init__(name)
        self.interval = interval

    def apply(self, query, value, model):
        if value:
            return query.filter(
                model.timestamp >= datetime.now(timezone.utc) - self.interval
            )
        return query


app = FastAPI()

register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL"),
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

admin = Admin()
user_question_view = ModelView(UserQuestion)
user_question_view.add_filter(TimestampFilter("Last 1 Hour", timedelta(hours=1)))
user_question_view.add_filter(TimestampFilter("Last 1 Day", timedelta(days=1)))
user_question_view.add_filter(TimestampFilter("Last 1 Month", timedelta(days=30)))
admin.add_view(user_question_view)
admin.mount_to(app)


@app.on_event("startup")
async def on_startup():
    await TortoiseAdmin.setup(admin)
