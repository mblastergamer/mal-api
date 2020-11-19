from typing import List

from mal import config
from mal.search import _Search, _SearchResult


class MangaSearchResult(_SearchResult):
    def __init__(
            self, mal_id, url, image_url, title, synopsis, media_type, volumes, score
    ):
        """
        Manga search result
        :param mal_id: MyAnimeList ID
        :param url: URL
        :param image_url: Image URL
        :param title: Title
        :param synopsis: Brief synopsis
        :param media_type: Type
        :param volumes: Volumes count
        :param score: Score
        """
        super().__init__(mal_id, url, image_url, title, synopsis, media_type, score)
        self.volumes = volumes


class MangaSearch(_Search):
    def __init__(self, query: str, timeout: int = config.TIMEOUT):
        """
        Manga search by query
        :param query: Query text
        :param timeout: Timeout in seconds
        """
        super().__init__(query, "manga", timeout)

    def reload(self) -> None:
        """
        Reload manga search
        :return: None
        """
        self.__init__(self._query)

    @property
    def results(self) -> List[MangaSearchResult]:
        """
        Get results
        :return: List of manga search results
        """
        try:
            self._results
        except AttributeError:
            trs = self._inner_page.find_all("tr")
            results = []
            for tr in trs[1:]:
                tds = tr.find_all("td")

                url = tds[0].find("a")["href"]
                mal_id = self._parse_mal_id(url)

                results.append(
                    MangaSearchResult(
                        mal_id=mal_id,
                        url=url,
                        image_url=self._extract_image_url(
                            tds[0].find("img")["data-src"]
                        ),
                        title=tds[1].find("strong").text.strip(),
                        synopsis=self._remove_suffix(
                            tds[1].find("div", {"class": "pt4"}).text.strip(),
                            "read more.",
                        ),
                        media_type=tds[2].text.strip(),
                        volumes=self._parse_eps_vols(tds[3].text),
                        score=self._parse_score(tds[4].text),
                    )
                )
            self._results = results
        return self._results
