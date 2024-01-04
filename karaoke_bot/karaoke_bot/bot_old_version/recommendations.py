from datetime import datetime
import random
from karaoke_bot.bot_old_version.unique_links_parse import load_links_by_user_id, get_unique_links

unique_links = get_unique_links('id_url_all.csv')
links_by_user_id = load_links_by_user_id('links_by_user_id.json')


class RandomRecommendation:

    def __init__(self,
                 url: str,
                 message_id: int,
                 user_id: int,
                 dt: datetime,
                 rec_type: str | None = None,
                 is_accepted: bool = False):
        self.url = url
        self.message_id = message_id
        self.user_id = user_id
        self.dt = dt
        self.rec_type = rec_type
        self.is_accepted = is_accepted


def get_recommendation_by_message_id(message_id: int) -> RandomRecommendation:
    for recommendation in recommendations:
        if recommendation.message_id == message_id:
            return recommendation


recommendations: list[RandomRecommendation] = []
