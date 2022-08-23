import uuid

import pytest

from db.models.user import User
from repository.users.user import UserRepository


@pytest.fixture()
def user_repository(db_session):
    return UserRepository(db_session)


@pytest.fixture()
async def already_exists_user(db_session, user_repository):
    return await user_repository.create(4895)


@pytest.fixture()
async def user_without_referrer(db_session, user_repository):
    return await user_repository.create(879234)


@pytest.fixture()
async def city_id(db_session):
    city_uuid = uuid.uuid4()
    await db_session.execute(
        "INSERT INTO cities (city_id, name) VALUES (:city_id, 'Казань') RETURNING city_id",
        {'city_id': str(city_uuid)},
    )
    return city_uuid


@pytest.fixture()
async def active_users(db_session, mixer, city_id):
    user_dicts = []
    users = mixer.cycle(5).blend(
        'db.models.user.User',
        is_active=True,
        chat_id=(chat_id for chat_id in range(1, 6)),
        city_id=str(city_id),
    )
    for user in users:
        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state')
        user_dicts.append(user_dict)
    await db_session.execute_many(
        User.__table__.insert(),
        values=user_dicts,
    )
    return [generated_user.chat_id for generated_user in users]


@pytest.fixture()
async def inactive_users(db_session, mixer):
    user_dicts = []
    users = mixer.cycle(7).blend(
        'db.models.user.User',
        is_active=False,
        chat_id=(chat_id for chat_id in range(6, 14)),
    )
    for user in users:
        user_dict = user.__dict__
        user_dict.pop('_sa_instance_state')
        user_dicts.append(user_dict)
    await db_session.execute_many(
        User.__table__.insert(),
        values=user_dicts,
    )
    return [generated_user.chat_id for generated_user in users]
