#from shared.gql_client import GraphQLClient, PaginationQueryResult
#from typing import Dict, Any
## This should be removed
#
#
#class DataSyncronizerQueries:
#    def __init__(
#        self,
#        deltas_query: str,
#        main_query_by_dbids: str,
#        main_query_by_cursor: str
#    ) -> None:
#        self.deltas_query = deltas_query
#        self.main_query_by_dbids = main_query_by_dbids
#        self.main_query_by_cursor = main_query_by_cursor
#
#
#class DeltasResult:
#    def __init__(self, additions: set, updates: set, deletions: set, last_cursor: str) -> None:
#        self.additions = additions
#        self.updates = updates
#        self.deletions = deletions
#        self.last_cursor = last_cursor
#
#    def has_additions(self) -> bool:
#        return len(self.additions) > 0
#    
#    def has_updates(self) -> bool:
#        return len(self.updates) > 0
#    
#    def has_deletions(self) -> bool:
#        return len(self.deletions) > 0
#    
#    def get_additions(self) -> list:
#        return list(self.additions)
#    
#    def get_updates(self) -> list:
#        return list(self.updates)
#    
#    def get_deletions(self) -> list:
#        return list(self.deletions)
#
#
#class DataSyncronizer:
#    def __init__(self, syncronizer_name: str, client: GraphQLClient, queries: DataSyncronizerQueries) -> None:
#        self.syncronizer_name = syncronizer_name
#        self.graphql_client = client
#        self.queries = queries
#
#        # These should be fetched from configuration manager.
#        # Maybe class for writing to data lake.
#        self.deltas_cursor = None
#        self.initial_sync_cursor = None
#        self.initial_sync_complete = True # Could be environment variable.
#
#        # Variables.
#
#
#    def syncronize_data(self) -> None:
#        if self.initial_sync_complete:
#            changed_items = self.get_all_changed_items()
#            
#            # flatten the data.
#            # write to data lake.
#            # update the deltas_cursor.
#        else:
#            self.get_all_deltas()
#            # 1. Get the very last deltas cursor.
#            # 2. Get all the data from the initial_sync_cursor.
#            # 3. If data fetch completes until initial_sync_complete:
#                # Set initial_sync_complate flag to true.
#                # Set initial sync cursosr to 0.
#            # 4. Get all deltas after the previously recorded deltas cursor.
#
#
#
#
#            last_syncversion = self.initial_sync_cursor
#            all_items = self.get_all_items()
#            all_nodes = all_items.get_nodes()
#            # flatten the data.
#            # write to data lake.
#            # update the initial_sync_cursor.
#            # update the initial_sync_complete.
#            #self._syncronize_initial_sync()
#
#    def get_all_deltas(self) -> DeltasResult:
#        query_result = self.graphql_client.paginate_gql_query(self.queries.deltas_query, {"first": 10000, "after": self.deltas_cursor})
#        deltas_result = self._extract_all_deltas_from_edges(query_result)
#        return deltas_result
#    
#    def get_last_delta(self) -> DeltasResult:
#        query_result = self.graphql_client.paginate_gql_query(self.queries.deltas_query, {"last": 1})
#        deltas_result = self._extract_all_deltas_from_edges(query_result)
#        return deltas_result
#    
#    def get_all_changed_items(self) -> PaginationQueryResult:
#        deltas_result = self.get_all_deltas()
#        all_changed_items = []
#
#        if deltas_result.has_additions():
#            query_results = self.graphql_client.paginate_gql_query(self.queries.main_query_by_dbids, {"first": 10000, "dbIdList": list(deltas_result.get_additions())})
#            query_results.add_key_to_all_nodes("mutationType", "ADDED")
#            all_changed_items.extend(query_results.get_nodes())
#
#        if deltas_result.has_updates():
#            query_results = self.graphql_client.paginate_gql_query(self.queries.main_query_by_dbids, {"first": 10000, "dbIdList": deltas_result.get_updates()})
#            query_results.add_key_to_all_nodes("mutationType", "UPDATED")
#            all_changed_items.extend(query_results.get_nodes())
#
#        for db_id in deltas_result.get_deletions():
#            all_changed_items.append({"dbId": db_id, "mutationType": "DELETED"}) 
#
#        return all_changed_items
#    
#    def get_all_items(self) -> PaginationQueryResult:
#        query_results = self.graphql_client.paginate_gql_query(self.queries.main_query_by_cursor, {"first": 10000, "after": self.initial_sync_cursor})
#        query_results.add_key_to_all_nodes("mutationType", "ADDED")
#        return query_results
#
#    def _process_changes(self, change_type: str, db_ids: list):
#        all_changed_items = []
#        if db_ids:
#            query_results = self.graphql_client.paginate_gql_query(self.queries.main_query_by_dbids, {"first": 10000, "dbIdList": db_ids})
#            query_results.add_key_to_all_nodes("mutationType", change_type)
#            all_changed_items.extend(query_results.get_nodes())
#        return all_changed_items
#
#    def _extract_all_deltas_from_edges(self, result: PaginationQueryResult) -> DeltasResult:
#        additions = set()
#        updates = set()
#        deletions = set()
#
#        edges = result.edges
#        if not edges:
#            return
#
#        for edge in edges:
#            mutation_type = edge['node']['mutationType']
#            db_id = edge['node']['dbId']
#
#            if mutation_type == "DELETED":
#                deletions.add(db_id)
#
#            elif mutation_type in ["UPDATED"]:
#                updates.add(db_id)
#
#            elif mutation_type in ["ADDED"]:
#                additions.add(db_id)
#
#            else:
#                raise ValueError(f"Unknown mutation type: {mutation_type}")
#
#        for db_id in deletions:
#            try: 
#                updates.remove(db_id)
#                additions.remove(db_id)
#            except KeyError:
#                pass
#
#        return DeltasResult(additions, updates, deletions, result.last_cursor)