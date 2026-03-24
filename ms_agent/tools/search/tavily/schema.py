# flake8: noqa
from typing import Any, Dict, List, Optional

from ms_agent.tools.search.search_base import (BaseResult, SearchRequest,
                                               SearchResponse, SearchResult)


class TavilySearchRequest(SearchRequest):
    """A class representing a search request to Tavily."""

    def __init__(self,
                 query: str,
                 num_results: Optional[int] = 5,
                 search_depth: Optional[str] = 'basic',
                 topic: Optional[str] = 'general',
                 **kwargs: Any):
        """
        Initialize TavilySearchRequest with search parameters.

        Args:
            query: The search query string
            num_results: Number of results to return, default is 5
            search_depth: Search depth, one of 'basic' or 'advanced'
            topic: Search topic, one of 'general', 'news', 'finance'
        """
        super().__init__(query=query, num_results=num_results, **kwargs)
        self.search_depth = search_depth
        self.topic = topic

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request parameters to a dictionary."""
        return {
            'query': self.query,
            'max_results': self.num_results,
            'search_depth': self.search_depth,
            'topic': self.topic,
        }


class TavilySearchResult(SearchResult):
    """Tavily search result implementation."""

    def __init__(self,
                 query: str,
                 arguments: Dict[str, Any] = None,
                 response: Any = None):
        """
        Initialize TavilySearchResult.

        Args:
            query: The original search query string
            arguments: The arguments used for the search
            response: The raw results returned by the search
        """
        super().__init__(query, arguments, response)
        if self.response is not None:
            self.response = self._process_results()

    def _process_results(self) -> SearchResponse:
        """Process the raw Tavily results into a standardized format."""
        results_list = self.response if isinstance(self.response, list) else self.response.get('results', [])

        if not results_list:
            print('***Warning: No search results found.')
            return SearchResponse(results=[])

        processed = []
        for res in results_list:
            processed.append(
                BaseResult(
                    url=res.get('url'),
                    id=res.get('url'),
                    title=res.get('title'),
                    highlights=None,
                    highlight_scores=[res.get('score')] if res.get('score') is not None else None,
                    summary=res.get('content'),
                    markdown=res.get('raw_content'),
                ))

        return SearchResponse(results=processed)
