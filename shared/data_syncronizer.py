from typing import List, Dict, Any, Optional
import logging
from shared.delta_fetcher import DeltaFetcher
from shared.item_fetcher import ItemFetcher
from shared.data_lake_writer import DataLakeWriter
from shared.configuration_manager import ConfigurationManager, SynchronizerStateManager
from shared.utils.data_transformation import add_key_value_to_dicts, flatten_list_of_dicts
from shared.utils.files import convert_dicts_to_parquet
from shared.utils.time import get_current_time_for_filename
import json


class ChangedItemsResult:
    def __init__(self, items: List[Dict[str, Any]], last_deltas_cursor: str):
        self.items = items
        self.last_deltas_cursor = last_deltas_cursor

    def has_changed_items(self) -> bool:
        return bool(self.items)


# This one will also have a data lake writer class.
class DataSynchronizer:
    def __init__(self, 
                 name: str, 
                 delta_fetcher: DeltaFetcher, 
                 item_fetcher: ItemFetcher,
                 data_lake_writer: DataLakeWriter,
                 state_manager: SynchronizerStateManager = None) -> None:
        self.name = name
        self.delta_fetcher = delta_fetcher
        self.item_fetcher = item_fetcher
        self.state_manager = state_manager
        self.data_lake_writer = data_lake_writer

    def syncronize(self) -> None:
        if not self.state_manager.initial_sync_complete:

            # Get the last delta.
            deltas = self.delta_fetcher.fetch_deltas({"last": 1})

            # Fetch all items.
            items = self.item_fetcher.fetch_all_items_after_cursor()
            if not items.has_items():
                logging.info(f"No items found for {self.name}.")
                return
            
            # Transform items.
            items.add_key_value_to_items("mutationType", "ADDED")
            items_transformed = convert_dicts_to_parquet(flatten_list_of_dicts(items.get_items()))
            
            # Write items to data lake.
            self.data_lake_writer.write_data("filesystem", self.name, f"{get_current_time_for_filename()}-{self.name}.parquet", items_transformed)

            # Update state.
            self.state_manager.initial_sync_cursor = items.get_last_item_cursor()
            self.state_manager.initial_sync_complete = True
            self.state_manager.deltas_cursor = deltas.last_cursor

        else:

            deltas = self.delta_fetcher.fetch_deltas({"first": 10000, "after": self.state_manager.deltas_cursor})
            if not deltas.has_changes():
                logging.info(f"No changes found for {self.name}.")
                return
            
            # Get all changed items based on the dbids fetc hed with the delta_fetcher.
            all_changed_items = []
            if deltas.has_additions():
                additions = self.item_fetcher.fetch_items_by_ids(deltas.get_additions())
                additions.add_key_value_to_items("mutationType", "ADDED")
                all_changed_items.extend(additions.get_items())

            if deltas.has_updates():
                updates = self.item_fetcher.fetch_items_by_ids(deltas.get_updates())
                updates.add_key_value_to_items("mutationType", "UPDATED")
                all_changed_items.extend(updates.get_items())

            if deltas.has_deletions():
                deletions = [{"dbId": dbId, "mutationType": "DELETED"} for dbId in deltas.get_deletions()]
                all_changed_items.extend(deletions)

            # Transform items.
            parquet = convert_dicts_to_parquet(flatten_list_of_dicts(all_changed_items))

            # Write items to data lake.
            self.data_lake_writer.write_data("filesystem", self.name, f"{get_current_time_for_filename()}-{self.name}.parquet", parquet)

            # Update state.
            self.state_manager.deltas_cursor = deltas.last_cursor
            
            # Get current time.
            # Get all items less than current time.
            # Get all changed items after current time.
            # Combine all items.
            # Write items to data lake.
            # Update state.
    def _get_all_items(self) -> None:
        items_result = self.item_fetcher.fetch_all_items_after_cursor()

    def _get_changed_items(self) -> ChangedItemsResult:
        deltas = self.delta_fetcher.fetch_deltas({"first": 10000, "after": self.state_manager.deltas_cursor})
        if not deltas.has_changes():
            return 
        raise NotImplementedError("Not implemented yet.")

    def _synchronize_from_deltas(self) -> tuple[List[Dict[str, Any]], str]:
        deltas = self.delta_fetcher.fetch_deltas({"first": 10000, "after": self.state_manager.deltas_cursor})
        if not deltas.has_changes():
            return []
        
        # Get all changed items based on the dbids fetched with the delta_fetcher.
        all_changed_items = []
        if deltas.has_additions():
            items_result = self.item_fetcher.fetch_items_by_ids(deltas.get_additions())
            items = items_result.get_items()
            addition_items = add_key_value_to_dicts(items, "mutationType", "ADDED")
            all_changed_items.extend(addition_items)

        if deltas.has_updates():
            items_results = self.item_fetcher.fetch_items_by_ids(deltas.get_updates())
            items = items_results.get_items()
            update_items = add_key_value_to_dicts(items, "mutationType", "UPDATED")
            all_changed_items.extend(update_items)
        
        if deltas.has_deletions():
            all_changed_items.extend([{dbId: dbId, "mutationType": "DELETED"} for dbId in deltas.get_deletions()])

        return all_changed_items, deltas.last_cursor

    def _transform_and_write_items(self, items: List[Dict[str, Any]]) -> None:
        flattened_items = flatten_list_of_dicts(items)
        parquet = convert_dicts_to_parquet(flattened_items)
        self.data_lake_writer.write_data("filesystem", self.name, f"{get_current_time_for_filename()}-{self.name}.parquet", parquet)

    def _syncronize_from_full(self) -> None:
        raise NotImplementedError("Full syncronization is not implemented yet.")

    #def _fetch_changed_items(self) -> ChangedItemsResult:
    #    # Fetch all deltas since last deltas sync cursor.
    #    deltas_result = self.delta_fetcher.fetch_deltas(
    #        {"first": 10000, "after": self.config_manager.get('deltas_cursor')})
    #    
    #    # If no new changes, return empty list.
    #    if not deltas_result.has_changes():
    #        ChangedItemsResult([], None)
#
    #    # Fetch all changed items.
    #    all_changed_items = []
    #    if deltas_result.has_additions():
    #        all_changed_items.extend(self.item_fetcher.fetch_items_by_ids(deltas_result.get_additions(), "ADDED"))
    #    
    #    if deltas_result.has_updates():
    #        all_changed_items.extend(self.item_fetcher.fetch_items_by_ids(deltas_result.get_updates(), "UPDATED"))
#
    #    if deltas_result.has_deletions():
    #        all_changed_items.extend({"dbIDd"}deltas_result.)  # Corrected
#
    #    return all_changed_items

    def _fetch_all_items(self) -> List[Dict[str, Any]]:
        query_results = self.item_fetcher.fetch_all_items(
            self.config_manager.get('initial_sync_cursor'))
        return add_key_value_to_dicts(query_results.get_nodes(), "ADDED")