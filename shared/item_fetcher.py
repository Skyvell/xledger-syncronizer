from shared.gql_client import GraphQLClient, PaginationQueryResult
from typing import Dict, Any, Set, List, Optional
import logging


class ItemsResult:
    def __init__(self, items: list[Dict], last_deltas_cursor: str = None) -> None:
        self.items = items
        self.last_deltas_cursor = last_deltas_cursor

    def has_items(self) -> bool:
        return bool(self.items)
    
    def get_items(self) -> List[Dict]:
        return self.items
    
    def get_last_deltas_cursor(self) -> str:
        return self.last_deltas_cursor
    
    def get_last_item_cursor(self) -> str:
        return self.items[-1]['cursor'] if self.items else None
    
    def add_key_to_all_items(self, key: str, value: Any) -> None:
        for item in self.items:
            item[key] = value


class ItemFetcher:
    def __init__(self, client: GraphQLClient, query_by_dbids: str, query_by_cursor: str) -> None:
        self.graphql_client = client
        self.query_by_dbids = query_by_dbids
        self.query_by_cursor = query_by_cursor

    def fetch_items_by_ids(self, db_ids: List[str], first: int = 10000) -> ItemsResult:
        if not db_ids:
            return ItemsResult([])
        
        variables = {"first": first, "dbIdList": db_ids}
        query_resut = self._execute_paginated_query(self.query_by_dbids, variables)
        return ItemsResult(query_resut.get_nodes(), query_resut.get_last_cursor())

    def fetch_all_items_after_cursor(self, after: Optional[str], first: int = 10000) -> PaginationQueryResult:
        variables = {"first": first, "after": after}
        return self._execute_paginated_query(self.query_by_cursor, variables)

    def _execute_paginated_query(self, query: str, variables: Dict[str, Any]) -> PaginationQueryResult:
        try:
            return self.graphql_client.paginate_gql_query(query, variables)
        except Exception as e:
            logging.error(f"Error fetching items: {e}")
            raise