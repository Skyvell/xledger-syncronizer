import logging
from typing import Dict, List, Any
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from tenacity import retry, stop_after_attempt, wait_exponential


class GraphQLQueryException(Exception):
    """Exception raised for errors in the GraphQL query execution."""
    pass


class PaginationQueryResult:
    """
    Class to encapsulate the results of a paginated GraphQL query.

    Attributes:
        edges (list): The list of edges (data items) returned by the query.
        last_cursor (str): The cursor for the last item fetched, used for pagination.
    """
    def __init__(self, edges: List[Dict[str, Any]]) -> None:
        self.edges = edges

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Returns the list of nodes (data items) extracted from the edges.

        :return: A list of nodes.
        """
        return [edge['node'] for edge in self.edges]
    
    def get_last_cursor(self) -> str:
        """
        Returns the cursor for the last item fetched.

        :return: The cursor for the last item.
        """
        return self.edges[-1]['cursor'] if self.edges else None
    
    def has_results(self) -> bool:
        return len(self.edges) > 0


class GraphQLClient:
    """
    A client to interact with a GraphQL API.

    Attributes:
        api_endpoint (str): The endpoint URL of the GraphQL API.
        api_key (str): The API key for authentication.
        client (Client): The gql Client instance for executing queries.
    """

    def __init__(self, api_endpoint: str, api_key: str):
        """
        Initializes the GraphQLClient with the given API endpoint and API key.

        :param api_endpoint: The endpoint URL of the GraphQL API.
        :param api_key: The API key for authentication.
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.client = self._create_client()

    def _create_client(self) -> Client:
        """
        Creates and returns a gql Client instance configured with the API endpoint and key.

        :return: A configured gql Client instance.
        """
        headers = {"Authorization": f"token {self.api_key}"}
        transport = AIOHTTPTransport(url=self.api_endpoint, headers=headers)
        return Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=60)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def execute_graphql_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a GraphQL query and returns the result.

        :param query: The GraphQL query string.
        :param variables: A dictionary of variables to be passed with the query.
        :return: A dictionary representing the query result.
        :raises GraphQLQueryException: If an error occurs during query execution.
        """
        try:
            logging.debug(f"Executing GraphQL query: {query} with variables: {variables}")
            return self.client.execute(query, variable_values=variables)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise GraphQLQueryException(f"An error occurred: {str(e)}")

    def paginate_gql_query(self, query: str, variables: Dict[str, Any]) -> PaginationQueryResult:
        """
        Fetches all data by paginating over a GraphQL query.

        :param query: The GraphQL query string that includes pagination.
        :param variables: Initial variables for the query, typically includes 'first' and optionally 'after'.
        :param query_name: The name of the query to extract results from the response.
        :return: A PaginationQueryResult containing all fetched items and the last cursor.
        :raises GraphQLQueryException: If the query execution fails or no data is found.
        """
        all_results = []
        last_cursor = None

        while True:
            try:
                # Execute the query.
                result = self.execute_graphql_query(query=query, variables=variables)
                query_name = next(iter(result))
                data = result.get(query_name)
                if not data:
                    raise GraphQLQueryException(f"No data found for query: {query_name}")

                # Extract the edges and last cursor form current page.
                edges = data.get('edges')
                if edges:
                    all_results.extend(data['edges'])
                    last_cursor = data['edges'][-1]['cursor']

                # Check if there is a next page.
                if not data['pageInfo']['hasNextPage']:
                    break

                # Update variables for the next page.
                variables['after'] = last_cursor

            except GraphQLQueryException:
                raise
            except Exception as e:
                logging.error(f"An error occurred during the GraphQL query execution: {e}")
                raise GraphQLQueryException(f"An error occurred during the GraphQL query execution: {e}")

        return PaginationQueryResult(edges=all_results)

    def __enter__(self):
        """Enable use of 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the client is properly closed."""
        self.client.transport.close()
