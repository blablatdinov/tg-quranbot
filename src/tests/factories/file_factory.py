import uuid


async def factory(db_session) -> uuid.UUID:
    file_id = uuid.uuid4()
    insert_file_query = """
        INSERT INTO files
        (file_id, telegram_file_id, created_at, link)
        VALUES
        (:file_id, 'fake_telegram_file_id', '2030-01-03', 'file/link')
    """
    await db_session.execute(insert_file_query, {'file_id': str(file_id)})
    return file_id
