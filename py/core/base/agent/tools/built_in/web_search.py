import logging
import os

from shared.abstractions.tool import Tool

logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """
    A web search tool that supports multiple providers (SerpApi, Serper) to perform
    Google searches and returns the most relevant results.
    """

    def __init__(self):
        super().__init__(
            name="web_search",
            description=(
                "Search for information on the web - use this tool when the user "
                "query needs LIVE or recent data from the internet."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search with an external web API.",
                    },
                },
                "required": ["query"],
            },
            results_function=self.execute,
            llm_format_function=None,
        )

    async def execute(self, query: str, *args, **kwargs):
        """
        Implementation of web search functionality.
        """
        import asyncio

        from core.base.abstractions import (
            AggregateSearchResult,
            WebSearchResult,
        )
        from core.utils.serper import SerperClient
        from core.utils.serpapi import SerpApiClient

        context = self.context

        # Try SerpApi first if SERPAPI_API_KEY is present,
        # or if we suspect the key in SERPER_API_KEY is actually a SerpApi key.
        # Given the current cluster state, we know the key in SERPER_API_KEY is SerpApi.
        serpapi_available = (
            os.getenv("SERPAPI_API_KEY") is not None
            or os.getenv("SERPER_API_KEY") is not None
        )
        use_serpapi = serpapi_available

        if use_serpapi:
            try:
                logger.info(f"Performing web search for '{query}' using SerpApi.")
                serpapi_client = SerpApiClient()
                raw_results = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: serpapi_client.get_raw(query),
                )
                web_response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: WebSearchResult.from_serpapi_results(raw_results)
                )
            except Exception as e:
                logger.error(f"SerpApi failed: {e}. Falling back to Serper.")
                use_serpapi = False

        if not use_serpapi:
            logger.info(f"Performing web search for '{query}' using Serper.")
            serper_client = SerperClient()
            raw_results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: serper_client.get_raw(query),
            )
            web_response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: WebSearchResult.from_serper_results(raw_results)
            )

        result = AggregateSearchResult(
            web_search_results=[web_response],
        )

        # Add to results collector if context is provided
        if context and hasattr(context, "search_results_collector"):
            context.search_results_collector.add_aggregate_result(result)

        return result
