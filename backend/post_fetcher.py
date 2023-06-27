from dataclasses import dataclass
import requests
import fastapi as _fastapi

from backend.logger import logger
from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.vkscript import GET_2500_POSTS_TEMPLATE


@dataclass
class PostFetcher:
    """
    Fetches posts from VK group or person.
    """

    domain: str  # Group or person address in VK, e.g. "a_a_burlakov"

    _total_posts: int = 0

    def _set_total_posts_in_domain(self) -> None:
        """Sets "_total_posts" as amount of posts in the VK domain."""
        logger.info(f'Getting total posts in "vk.com/{self.domain}"...')

        params = {
            "v": VKAPI_VERSION,
            "access_token": VKAPI_TOKEN,
            "count": 1,
            "domain": self.domain,
        }

        response = requests.get(VKAPI_URL + "wall.get", params=params).json()
        if "error" in response:
            raise _fastapi.HTTPException(
                status_code=500, detail=response["error"]["error_msg"]
            )

        self._total_posts = response["response"]["count"]
        logger.info(f"Total posts in VK domain: {self._total_posts}")

    def fetch_posts_synchronously(self) -> list:
        """
        Fetches posts from VK domain synchronously.
        :return: a list of posts in the VK domain.
        """
        fetched_posts: list = []
        self._set_total_posts_in_domain()

        logger.info(f'Start fetching posts from "vk.com/{self.domain}"...')

        current_offset = 0
        while len(fetched_posts) < self._total_posts:
            vks_code = GET_2500_POSTS_TEMPLATE.substitute(
                {"domain": self.domain, "offset": current_offset}
            )
            params = {"v": VKAPI_VERSION, "access_token": VKAPI_TOKEN, "code": vks_code}
            response = requests.get(VKAPI_URL + "execute", params=params).json()

            if "error" in response:
                raise _fastapi.HTTPException(
                    status_code=500, detail=response["error"]["error_msg"]
                )
            fetched_posts.extend(response["response"]["items"])
            current_offset += 2500

        return fetched_posts