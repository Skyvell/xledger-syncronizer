from shared.gql_client import GraphQLClient, PaginationQueryResult
from typing import Dict, Any
import logging


class DeltasResult:
    def __init__(self, additions: set, updates: set, deletions: set, last_cursor: str) -> None:
        self.additions = additions
        self.updates = updates
        self.deletions = deletions
        self.last_cursor = last_cursor

    def has_changes(self) -> bool:
        return bool(self.additions or self.updates or self.deletions)

    def has_additions(self) -> bool:
        return len(self.additions) > 0
    
    def has_updates(self) -> bool:
        return len(self.updates) > 0
    
    def has_deletions(self) -> bool:
        return len(self.deletions) > 0
    
    def get_additions(self) -> list:
        return list(self.additions)
    
    def get_updates(self) -> list:
        return list(self.updates)
    
    def get_deletions(self) -> list:
        return list(self.deletions)
    

class DeltaFetcher:
    def __init__(self, client: GraphQLClient, query: str) -> None:
        self.graphql_client = client
        self.query = query

    def fetch_deltas(self, variables: Dict[str, Any]) -> DeltasResult:
        try:
            query_result = self._execute_paginated_query(variables)
            return self._extract_deltas(query_result)
        except Exception as e:
            logging.error(f"Error fetching deltas: {e}")
            raise

    def _execute_paginated_query(self, variables: Dict[str, Any]) -> PaginationQueryResult:
        return self.graphql_client.paginate_gql_query(self.query, variables)

    def _extract_deltas(self, result: PaginationQueryResult) -> DeltasResult:
        additions = set()
        updates = set()
        deletions = set()

        if not result.has_results():
            return DeltasResult(additions, updates, deletions, result.get_last_cursor())

        for edge in result.edges:
            node = edge['node']
            mutation_type = node.get('mutationType')
            db_id = node.get('dbId')

            if mutation_type == "DELETED":
                deletions.add(db_id)
            elif mutation_type == "UPDATED":
                updates.add(db_id)
            elif mutation_type == "ADDED":
                additions.add(db_id)

        updates -= deletions
        additions -= deletions

        return DeltasResult(additions, updates, deletions, result.get_last_cursor())
