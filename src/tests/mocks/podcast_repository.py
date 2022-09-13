from repository.podcast import PodcastRepositoryInterface, RandomPodcast


class PodcastRepositoryMock(PodcastRepositoryInterface):

    async def get_random(self) -> RandomPodcast:
        return RandomPodcast(audio_telegram_id='file_id', link_to_audio_file='https://link.to.file')
