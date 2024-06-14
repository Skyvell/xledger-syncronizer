from azure import functions as func
import logging
import os

from shared.data_lake_writer import DataLakeWriter
from shared.configuration_manager import SynchronizerStateManager
from shared.delta_fetcher import DeltaFetcher
from shared.item_fetcher import ItemFetcher
from shared.data_syncronizer import DataSynchronizer
from shared.gql_client import GraphQLClient

from functions.timesheets.queries import (
    GET_TIMESHEET_DELTAS,
    GET_TIMESHEETS_AFTER_CURSOR,
    GET_TIMESHEETS_FROM_DBIDS
)


NAME = "timesheets_test2"

logging.basicConfig(level=logging.INFO)

bp = func.Blueprint()

@bp.function_name("SyncronizeTimesheets")
@bp.schedule(schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def syncronize_timesheets(myTimer: func.TimerRequest) -> None:
    # Get environment variables.
    api_endpoint = os.getenv("Endpoint")
    api_key = os.getenv("APIKey")
    data_lake_account_name = os.getenv("DataLakeAccountName")
    data_lake_account_key = os.getenv("DataLakeAccountKey")
    state_manager_connection_string = os.getenv("StateManagerConnectionString")

    # Initialize classes needed for syncronizing data.
    grapql_client = GraphQLClient(api_endpoint, api_key)
    data_lake_writer = DataLakeWriter(data_lake_account_name, data_lake_account_key)
    delta_fetcher = DeltaFetcher(grapql_client, GET_TIMESHEET_DELTAS)
    item_fetcher = ItemFetcher(grapql_client, GET_TIMESHEETS_FROM_DBIDS, GET_TIMESHEETS_AFTER_CURSOR)
    state_manager = SynchronizerStateManager(state_manager_connection_string, f"{NAME}-")

    # Initialize the data syncronizer.
    syncronizer = DataSynchronizer(
        NAME, 
        delta_fetcher,
        item_fetcher,
        data_lake_writer,
        state_manager
    )

    # Syncronize the data.
    syncronizer.syncronize()