# flake8: noqa
import os
from typing import TYPE_CHECKING

from ms_agent.tools.search.search_base import SearchEngine, SearchEngineType
from ms_agent.tools.search.tavily.schema import (TavilySearchRequest,
                                                  TavilySearchResult)

if TYPE_CHECKING:
    from ms_agent.llm.utils import Tool


class TavilySearch(SearchEngine):
    """
    Search engine using Tavily API.

    Best for: AI-optimized web search, real-time information retrieval,
    general web search with high relevance scoring.
    """

    engine_type = SearchEngineType.TAVILY

    def __init__(self, api_key: str = None):

        api_key = api_key or os.getenv('TAVILY_API_KEY')
        assert api_key, 'TAVILY_API_KEY must be set either as an argument or as an environment variable'

        from tavily import TavilyClient
        self.client = TavilyClient(api_key=api_key)

    def search(self,
               search_request: TavilySearchRequest) -> TavilySearchResult:
        """
        Perform a search using the Tavily API with the provided search request parameters.

        :param search_request: An instance of TavilySearchRequest containing search parameters.
        :return: An instance of TavilySearchResult containing the search results.
        """
        search_args: dict = search_request.to_dict()
        try:
            response = self.client.search(**search_args)
            return TavilySearchResult(
                query=search_request.query,
                arguments=search_args,
                response=response,
            )
        except Exception as e:
            raise RuntimeError(f'Failed to perform search: {e}') from e

    @classmethod
    def get_tool_definition(cls, server_name: str = 'web_search') -> 'Tool':
        """Return the tool definition for Tavily search engine."""
        from ms_agent.llm.utils import Tool
        return Tool(
            tool_name=cls.get_tool_name(),
            server_name=server_name,
            description=(
                'Search the web using Tavily AI-optimized search engine. '
                'Best for: general web search, real-time information, '
                'news, and research queries with high relevance scoring. '
                'Supports topic filtering and domain filtering.'),
            parameters={
                'type': 'object',
                'properties': {
                    'query': {
                        'type':
                        'string',
                        'description':
                        'The search query. Use natural language for best results.',
                    },
                    'num_results': {
                        'type':
                        'integer',
                        'minimum':
                        1,
                        'maximum':
                        10,
                        'description':
                        'Number of results to return. Default is 5.',
                    },
                    'search_depth': {
                        'type':
                        'string',
                        'enum': ['basic', 'advanced'],
                        'description':
                        ('Search depth. "basic" for fast results, '
                         '"advanced" for more thorough search. '
                         'Default is "advanced".'),
                    },
                    'topic': {
                        'type':
                        'string',
                        'enum': ['general', 'news', 'finance'],
                        'description':
                        ('Topic category for the search. '
                         'Default is "general".'),
                    },
                },
                'required': ['query'],
            },
        )

    @classmethod
    def build_request_from_args(cls, **kwargs) -> TavilySearchRequest:
        """Build TavilySearchRequest from tool call arguments."""
        return TavilySearchRequest(
            query=kwargs['query'],
            num_results=kwargs.get('num_results', 5),
            search_depth=kwargs.get('search_depth', 'advanced'),
            topic=kwargs.get('topic', 'general'),
            include_domains=kwargs.get('include_domains'),
            exclude_domains=kwargs.get('exclude_domains'),
        )
