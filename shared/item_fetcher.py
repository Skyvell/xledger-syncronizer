from shared.gql_client import GraphQLClient, PaginationQueryResult
from shared.utils.data_transformation import add_key_value_to_dicts
from typing import Dict, Any, Set, List
import logging


class ItemsResult:
    def __init__(self, items: list[Dict], cursor: str) -> None:
        self.items = items
        self.cursor = cursor

    def has_items(self) -> bool:
        return bool(self.items)
    
    def get_items(self) -> List[Dict]:
        return self.items
    
    def get_last_item_cursor(self) -> str:
        return self.cursor
    
    def add_key_value_to_items(self, key: str, value: Any) -> None:
        add_key_value_to_dicts(self.items, key, value)


class ItemFetcher:
    def __init__(self, client: GraphQLClient, query_by_dbids: str, query_by_cursor: str) -> None:
        self.graphql_client = client
        self.query_by_dbids = query_by_dbids
        self.query_by_cursor = query_by_cursor

    def fetch_items_by_ids(self, db_ids: List[str], first: int = 10000) -> ItemsResult:
        if not db_ids:
            return ItemsResult([], None)
        
        variables = {"first": first, "dbIdList": db_ids}
        query_result = self._execute_paginated_query(self.query_by_dbids, variables)

        return ItemsResult(query_result.get_nodes(), query_result.get_last_cursor())

    def fetch_all_items_after_cursor(self, after: str = None, first: int = 10000) -> ItemsResult:
        variables = {"first": first, "after": after}
        query_result = self._execute_paginated_query(self.query_by_cursor, variables)
        return ItemsResult(query_result.get_nodes(), query_result.get_last_cursor())

    def _execute_paginated_query(self, query: str, variables: Dict[str, Any]) -> PaginationQueryResult:
        try:
            return self.graphql_client.paginate_gql_query(query, variables)
        except Exception as e:
            logging.error(f"Error fetching items: {e}")
            raise