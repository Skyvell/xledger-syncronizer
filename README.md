## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Running the Application](#running-the-application)
5. [Usage](#usage)
    - [API Endpoints](#api-endpoints)
    - [GraphQL Queries](#graphql-queries)
    - [File Outputs](#file-outputs)
6. [Deployment](#deployment)
    - [Development Environment](#development-environment)
    - [Production Environment](#production-environment)
7. [Infrastructure as Code (IaC)](#infrastructure-as-code-iac)
8. [Testing](#testing)
9. [Contributing](#contributing)
10. [License](#license)
11. [Contact](#contact)

---

## Overview

Data Ductus is migrating from Brilliant to Xledger as a business system. The data stored with Xledger is needed for internal business analytics. This app will fetch the necessary business data from Xledger's GraphQL API and write the data to a Data Lake as .parquet files. This raw data will be transformed and loaded into a structure more suitable for business analytics, but that is not within the scope of this application. The scope of this application is to produce and keep the raw data synchronized in the Data Lake. The application is built on Azure serverless infrastructure.

## Features

- **Timesheets**: Perform a full load of all timesheets data and keep it synchronized.
- **Projects**: Perform a full load of all projects data and keep it synchronized.
- **Employees**: Perform a full load of all employees' data and keep it synchronized.
- **Customers**: Perform a full load of all customers' data and keep it synchronized.

## Architecture

The app is developed as a function app in Azure (Figure 1). It will consist of several Azure functions and associated triggers. Each function will be responsible for fetching and keeping a particular type of data synchronized in the Data Lake. For example, one function will be responsible for timesheets data, and another one for projects data. An App Configuration component will be used to store the state of the synchronization.

![Azure architecture](architecture/azure_architecture.svg)

*Figure 1: High-level architecture showing the flow of data from timers to Azure Functions and the Data Lake. The illustration only shows one function, but the function app will have a timer and function for each type of business data.*

## Getting Started

### Prerequisites

List the software and tools required to run the project. For example:

- [Node.js](https://nodejs.org/)
- [npm](https://www.npmjs.com/)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Terraform](https://www.terraform.io/)



## Usage

### Endpoint

### GraphQL queries

### File outputs
The files are written to a Datalake. When performing a full load of all the data, all data is written to one file. Next time when data is syncronized, changes will be in a new file. Files are named in a standardised nammed. Here are a few examples:
<pre>
<code>
`20240610_11_47_40_employees.parquet`
`20240610_15_39_09_employees.parquet`
`20240610_15_40_22_employees.parquet`
`20240610_11_47_34_customers.parquet`
`20240610_15_40_38_customers.parquet`
`20240611_13_27_39_customers.parquet`
</code>
</pre>

Question/thought: Maybe full load files should be named differently. Maybe syncronization or full_load should be prefixed.

## Deployment

### Development

### Production

## Infrastructure as code

## Testing

## License

## Contact
