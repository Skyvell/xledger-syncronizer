from gql import gql


GET_CUSTOMERS_FROM_DBIDS = gql("""
    query getCustomers($first: Int, $after: String, $dbIdList: [Int!]) {
        customers(
            first: $first, 
            after: $after, 
            filter: { dbId_in: $dbIdList }
        ) {
            edges {
                cursor
                node {
                    email
                    code
                    description
                    dbId
                    company {
                        name
                    }
                }
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")

GET_CUSTOMER_DELTAS = gql("""
    query getCustomerDeltas($first: Int, $after: String) {
        customer_deltas(
            first: $first, 
            after: $after
        ) {
            edges {
                node {
                    dbId
                    mutationType
                }
                cursor
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")