from azure import functions as func
import os

from shared.data_lake_writer import DataLakeWriter
from shared.configuration_manager import SynchronizerStateManager
from shared.delta_fetcher import DeltaFetcher
from shared.item_fetcher import ItemFetcher
from shared.data_syncronizer import DataSynchronizer
from shared.gql_client import GraphQLClient

from functions.employees.queries import (
    GET_EMPLOYEE_DELTAS,
    GET_EMPLOYEES_AFTER_CURSOR,
    GET_EMPLOYEES_FROM_DBIDS
)


NAME = "employees"

bp = func.Blueprint()


@bp.function_name("SyncronizeEmployees")
@bp.schedule(schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def syncronize_employees(myTimer: func.TimerRequest) -> None:
    # Get environment variables.
    api_endpoint = os.getenv("Endpoint")
    api_key = os.getenv("APIKey")
    data_lake_account_name = os.getenv("DataLakeAccountName")
    data_lake_account_key = os.getenv("DataLakeAccountKey")
    state_manager_connection_string = os.getenv("StateManagerConnectionString")

    # Initialize classes needed for syncronizing data.
    grapql_client = GraphQLClient(api_endpoint, api_key)
    data_lake_writer = DataLakeWriter(data_lake_account_name, data_lake_account_key)
    delta_fetcher = DeltaFetcher(grapql_client, GET_EMPLOYEE_DELTAS)
    item_fetcher = ItemFetcher(grapql_client, GET_EMPLOYEES_FROM_DBIDS, GET_EMPLOYEES_AFTER_CURSOR)
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
    if not syncronizer.state_manager.initial_sync_complete:
        syncronizer.syncronize(sync_from_scratch = True)
    else:
        syncronizer.syncronize(sync_from_scratch = False)