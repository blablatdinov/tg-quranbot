import asyncio

from integrations.tg.app import PollingApp
from integrations.tg.polling_updates import (
    PollingUpdatesIterator,
    UpdatesLongPollingURL,
    UpdatesTimeout,
    UpdatesURL,
    UpdatesWithOffsetURL,
)
from integrations.tg.sendable import SendableAnswer
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from settings import settings


def main():
    """Точка входа в приложение."""
    empty_answer = TgEmptyAnswer(settings.API_TOKEN)
    app = PollingApp(
        PollingUpdatesIterator(
            UpdatesLongPollingURL(
                UpdatesWithOffsetURL(
                    UpdatesURL(settings.API_TOKEN),
                ),
                UpdatesTimeout(),
            ),
            UpdatesTimeout(),
        ),
        SendableAnswer(
            TgTextAnswer(
                TgAnswerToSender(
                    TgMessageAnswer(empty_answer),
                ),
                'hello',
            ),
        ),
    ).run()
    asyncio.run(app)


if __name__ == '__main__':
    main()
