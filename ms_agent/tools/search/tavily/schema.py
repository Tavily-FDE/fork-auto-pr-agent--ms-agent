# flake8: noqa
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ms_agent.tools.search.search_base import (BaseResult, SearchRequest,
                                               SearchResponse, SearchResult)


class TavilySearchRequest(SearchRequest):
    """
    A class representing a search request to Tavily.
    """

    def __init__(self,
                 query: str,
                 num_results: Optional[int] = 5,
                 search_depth: Optional[str] = 'advanced',
                 topic: Optional[str] = 'general',
                 include_domains: Optional[List[str]] = None,
                 exclude_domains: Optional[List[str]] = None,
                 **kwargs: Any):
        """
        Initialize TavilySearchRequest with search parameters.

        Args:
            query: The search query string
            num_results: Number of results to return, default is 5
            search_depth: Search depth ('basic' or 'advanced'), default is 'advanced'
            topic: Topic category ('general', 'news', 'finance'), default is 'general'
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
        """
        super().__init__(query=query, num_results=num_results, **kwargs)
        self.search_depth = search_depth
        self.topic = topic
        self.include_domains = include_domains
        self.exclude_domains = exclude_domains

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the request parameters to a dictionary.

        Returns:
            Dict[str, Any]: The parameters as a dictionary
        """
        d = {
            'query': self.query,
            'max_results': self.num_results,
            'search_depth': self.search_depth,
            'topic': self.topic,
        }
        if self.include_domains:
            d['include_domains'] = self.include_domains
        if self.exclude_domains:
            d['exclude_domains'] = self.exclude_domains
        return d


class TavilySearchResult(SearchResult):
    """Tavily search result implementation."""

    def __init__(self,
                 query: str,
                 arguments: Dict[str, Any] = None,
                 response: Dict[str, Any] = None):
        """
        Initialize TavilySearchResult.

        Args:
            query: The original search query string
            arguments: The arguments used for the search
            response: The raw results returned by the search
        """
        super().__init__(query, arguments, response)
        self.response = self._process_results()

    def _process_results(self) -> SearchResponse:
        """
        Process the raw results into a standardized format.

        Returns:
            SearchResponse: Processed search results
        """
        if not self.response or not self.response.get('results'):
            print('***Warning: No search results found.')
            return SearchResponse(results=[])

        processed = []
        for res in self.response.get('results', []):
            processed.append(
                BaseResult(
                    url=res.get('url'),
                    id=res.get('url'),
                    title=res.get('title'),
                    highlights=None,
                    highlight_scores=[res.get('score')]
                    if res.get('score') is not None else None,
                    summary=res.get('content'),
                    markdown=res.get('raw_content'),
                ))

        return SearchResponse(results=processed)
