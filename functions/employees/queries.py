from gql import gql


GET_EMPLOYEES_FROM_DBIDS = gql("""
    query getEmployees($first: Int, $after: String, $dbIdList: [Int64String!]) {
        employees(
            first: $first,
            after: $after, 
            filter: { 
                dbId_in: $dbIdList
            }
        ) {
            edges {
                cursor
                node {
                    email
                    description
                    employmentType {
                        description
                        owner {
                            description
                        }
                    }
                    contact {
                        age
                        country {
                            description
                        }
                        firstName
                        lastName
                        gender {
                            name
                        }
                    }
                    exitReason {
                        description
                        code
                    }
                    glObject1 {
                        id
                        description
                    }
                    code
                }
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")

GET_EMPLOYEES_AFTER_CURSOR = gql("""
    query getEmployees($first: Int, $after: String) {
        employees(
            first: $first,
            after: $after
        ) {
            edges {
                cursor
                node {
                    email
                    description
                    employmentType {
                        description
                        owner {
                            description
                        }
                    }
                    contact {
                        age
                        country {
                            description
                        }
                        firstName
                        lastName
                        gender {
                            name
                        }
                    }
                    exitReason {
                        description
                        code
                    }
                    glObject1 {
                        id
                        description
                    }
                    code
                }
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")

GET_EMPLOYEE_DELTAS = gql("""
    query getEmployeeDeltas($first: Int, $last: Int, $after: String) {
        employee_deltas(
            first: $first,
            last: $last,
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