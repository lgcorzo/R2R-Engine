import json
import logging
import os
import urllib.parse
from http.client import HTTPSConnection

logger = logging.getLogger(__name__)


class SerpApiClient:
    def __init__(self, api_base: str = "serpapi.com") -> None:
        api_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError(
                "Please set the `SERPAPI_API_KEY` environment variable to use `SerpApiClient`."
            )

        self.api_base = api_base
        self.api_key = api_key

    def get_raw(self, query: str, limit: int = 10) -> list:
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": limit,
            "source": "r2r",
        }
        url_params = urllib.parse.urlencode(params)
        
        connection = HTTPSConnection(self.api_base)
        connection.request("GET", f"/search?{url_params}")
        
        response = connection.getresponse()
        if response.status != 200:
            logger.error(f"SerpApi returned status {response.status}: {response.read().decode()}")
            return []

        data = response.read()
        json_data = json.loads(data.decode("utf-8"))
        
        return self._extract_results(json_data)

    def _extract_results(self, json_data: dict) -> list:
        results = []
        
        # Organic results
        if "organic_results" in json_data:
            for res in json_data["organic_results"]:
                res["type"] = "organic"
                results.append(res)
                
        # Related searches
        if "related_searches" in json_data:
            for res in json_data["related_searches"]:
                res["type"] = "relatedSearches"
                results.append(res)
                
        # People also ask
        if "questions_and_answers" in json_data:
            for res in json_data["questions_and_answers"]:
                res["type"] = "peopleAlsoAsk"
                results.append(res)
        elif "related_questions" in json_data:
             for res in json_data["related_questions"]:
                res["type"] = "peopleAlsoAsk"
                results.append(res)

        return results
