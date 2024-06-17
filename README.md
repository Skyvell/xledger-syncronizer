# Project Name

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

Data Ductus is migrating from Brilliant to Xledger as a business system. The data stored with Xledger is needed for internal business analytics. This app will fetch the nessesary business data from Xledger's Graphql API, and write the data to a Datalake as .parquet files. This raw-data will be be transformed and loaded into a structure more suitable for business analytics, but that is not in the scope of this application. The scope of this application is to produce and keep the raw-data syncronized in the Datalake. The application is built on Azure serverless infrastructure.

## Features

- **Timesheets**: Perform a full load of all timesheets data and keep it syncronized.
- **Projects**: Perform a full load of all projects data and keep it syncronized.
- **Employees**: Perform a full load of all employes data and keep it syncronized.
- **Customers**: Perform a full load of all customers data and keep it syncronized.

## Architecture

The app is developed as a function app in Azure (Figure 1). It will consist of a number of azure function and associated triggers. Each function will be responsible for fetching and keeping a particular type of data syncronized in the Datalake. E.g. one function will be responsible for timesheets data, and another one for projects data. An App Configuration component will be used to store the state of the syncronization, since azure functions are stateless. 

![Azure architecture](architecture/azure_architecture.svg)

*Figure 1: High-level architecture showing the flow of data from timers to Azure Functions and the Data Lake. The illustration only shows one function, but the function app will have an timer and function for each type of business data.*

Provide an overview of the architecture. Include a diagram (e.g., a flowchart or system architecture diagram) to illustrate the components and their interactions.

### Diagram Description

- **Timers**: Describe how timers trigger functions.
- **Functions**: Explain what each function does.
- **GraphQL Endpoints**: Detail the data sources.
- **Data Lake**: Describe how data is stored.

## Getting Started

### Prerequisites

List the software and tools required to run the project. For example:

- [Node.js](https://nodejs.org/)
- [npm](https://www.npmjs.com/)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Terraform](https://www.terraform.io/)

### Installation

Provide step-by-step instructions on how to set up the project locally.

```bash
# Clone the repository
git clone https://github.com/yourusername/yourproject.git

# Navigate to the project directory
cd yourproject

# Install dependencies
npm install
