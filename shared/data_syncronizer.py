from typing import List, Dict, Any
import logging
from shared.delta_fetcher import DeltaFetcher
from shared.item_fetcher import ItemFetcher
from shared.data_lake_writer import DataLakeWriter
from shared.configuration_manager import SynchronizerStateManager
from shared.utils.data_transformation import flatten_list_of_dicts
from shared.utils.files import convert_dicts_to_parquet
from shared.utils.time import get_current_time_for_filename


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

    def syncronize(self, sync_from_scratch: bool) -> None:
        if sync_from_scratch:
            self._full_syncronization()
        else:
            self._syncronize_changes()

    def _full_syncronization(self) -> None:
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

    def _syncronize_changes(self) -> None:
        # Get all deltas since last sync.
        deltas = self.delta_fetcher.fetch_deltas({"first": 10000, "after": self.state_manager.deltas_cursor})

        # No new changes found -> return.
        if not deltas.has_changes():
            logging.info(f"No changes found for {self.name}.")
            return
        
        # Get all items based from the dbids fetched with the delta_fetcher.
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
