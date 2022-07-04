from repository.podcast import Podcast, PodcastRepositoryInterface


class PodcastRepositoryMock(PodcastRepositoryInterface):

    async def get_random(self) -> Podcast:
        return Podcast(audio_telegram_id='file_id', link_to_audio_file='https://link.to.file')
