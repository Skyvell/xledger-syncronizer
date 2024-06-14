from gql import gql 


GET_TIMESHEETS_FROM_DBIDS = gql("""
    query getTimesheets($first: Int, $after: String, $dbIdList: [Int64String!]) {
        timesheets(
            first: $first,
            after: $after, 
            filter: { 
                dbId_in: $dbIdList
            }
        ) {
            edges {
                node {
                    dbId
                    assignmentDate
                    isHeaderApproved
                    headerApprovedAt
                    owner {
                        description
                        dbId
                    }
                    employee {
                        code
                        description
                        dbId
                    }
                    activity {
                        code
                        description
                    }
                    timeType {
                        code
                        description
                    }
                    workingHours
                    assignmentDate
                }
                cursor
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")

GET_TIMESHEETS_AFTER_CURSOR = gql("""
    query getTimesheets($first: Int, $after: String) {
        timesheets(
            first: $first,
            after: $after
        ) {
            edges {
                node {
                    dbId
                    assignmentDate
                    isHeaderApproved
                    headerApprovedAt
                    owner {
                        description
                        dbId
                    }
                    employee {
                        code
                        description
                        dbId
                    }
                    activity {
                        code
                        description
                    }
                    timeType {
                        code
                        description
                    }
                    workingHours
                    assignmentDate
                }
                cursor
            }
            pageInfo {
                hasNextPage
            }
        }
    }
""")

GET_TIMESHEET_DELTAS = gql("""
    query getTimesheetDeltas($first: Int, $last: Int, $after: String) {
        timesheet_deltas(
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