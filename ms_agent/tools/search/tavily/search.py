import os

from ms_agent.tools.search.search_base import SearchEngine, SearchEngineType
from ms_agent.tools.search.tavily.schema import TavilySearchRequest, TavilySearchResult


class TavilySearch(SearchEngine):
    """Search engine implementation using the Tavily API."""

    engine_type = SearchEngineType.TAVILY

    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv('TAVILY_API_KEY')
        assert api_key, 'TAVILY_API_KEY must be set either as an argument or as an environment variable'
        from tavily import TavilyClient
        self.client = TavilyClient(api_key=api_key)

    def search(self, search_request: TavilySearchRequest) -> TavilySearchResult:
        """Perform a search using Tavily and return results."""
        search_args: dict = search_request.to_dict()
        search_result = TavilySearchResult(
            query=search_request.query,
            arguments=search_args,
        )
        try:
            response = self.client.search(**search_args)
            search_result.response = response
            # Re-process now that we have the response
            search_result.response = search_result._process_results()
        except Exception as e:
            raise RuntimeError(f'Failed to perform Tavily search: {e}') from e
        return search_result

    @classmethod
    def get_tool_definition(cls, server_name: str = 'web_search'):
        from ms_agent.llm.utils import Tool
        return Tool(
            tool_name=cls.get_tool_name(),
            server_name=server_name,
            description='Search the web using Tavily search engine.',
            parameters={
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query.',
                    },
                    'num_results': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 20,
                        'description':
                        'Number of results to return (default: 5).',
                    },
                    'search_depth': {
                        'type': 'string',
                        'enum': ['basic', 'advanced'],
                        'description':
                        "Search depth: 'basic' for fast results, 'advanced' for highest relevance.",
                    },
                    'topic': {
                        'type': 'string',
                        'enum': ['general', 'news', 'finance'],
                        'description':
                        "Search topic category (default: 'general').",
                    },
                },
                'required': ['query'],
            },
        )

    @classmethod
    def build_request_from_args(cls, **kwargs) -> TavilySearchRequest:
        return TavilySearchRequest(
            query=kwargs['query'],
            num_results=kwargs.get('num_results', 5),
            search_depth=kwargs.get('search_depth', 'basic'),
            topic=kwargs.get('topic', 'general'),
        )
