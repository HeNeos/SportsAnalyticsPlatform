# Sports Analytics Platform

## Setup

Modify the file `app.ts` to put your `AWS_ACCOUNT_ID` and setup your `AWS_ACCESS_KEY`s for programmatic access.

To manually create a virtualenv on MacOS and Linux:

``` bash
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

``` bash
source .venv/bin/activate
```

``` bash
pip install -r requirements.txt
```
## Deployment

### Manually

1. Run `cdk synth`
2. Run `cdk deploy DynamoDBStack`
3. Run `cdk deploy PostDataStack`
4. Run `cdk deploy GetDataStack`

### Scripting

Run the script `run.py`:
```bash
python run.py
```
The script performs the next actions:

1. Create a virtual python environment called `.venv` and install the packages and dependencies from `requirements.txt`.
3. Run `cdk synth`.
4. Run `cdk deploy DynamoDBStack`.
    - Creates the DynamoDB table for data storage.
    - Creates the Lambda function `data_processing` that calculates the statistics.
5. Run `cdk deploy PostDataStack`.
    - Deploys the Lambda function responsible for data ingestion and sets up the associated API Gateway endpoint.
6. Run `cdk deploy GetDataStack`.
    - Deploys the Lambda function responsible for data retrieval and sets up the associated API Gateway for data retrieval.

Enjoy!

## Overview

1. **Data Ingestion**:
   - The application allows real-time sports data to be ingested through an API Gateway endpoint.
   - Users can send JSON payloads representing match events to the API. Each payload includes details such as the match ID, timestamp, team names, event type (e.g., goal, foul), and event-specific details (e.g., player information, goal type, video URL).

2. **DynamoDBStack**:
   - The `DynamoDBStack` is a CDK stack responsible for creating and configuring the DynamoDB table used for data storage.
   - The table is configured to have a stream enabled, which captures a chronological sequence of item-level modifications (INSERTs and UPDATEs) to the table.

3. **PostDataStack**:
   - The `PostDataStack` is a CDK stack responsible for deploying the Lambda function that handles data ingestion.
   - The Lambda function is triggered whenever new data is sent to the API Gateway.
   - The Lambda function processes the incoming data, extracts relevant information, and inserts it into the DynamoDB table.
   - After successful data ingestion, the Lambda function returns a response indicating the success and relevant details of the inserted data.

4. **Data Processing Lambda**:
   - There is another Lambda function responsible for data processing. This Lambda function is triggered by the DynamoDB table stream, specifically when new data is inserted or updated in the table.
   - The data processing Lambda calculates statistics and other information based on the incoming match events. For example, it computes the total number of goals scored by each team, the number of fouls, etc.
   - The calculated statistics are stored in a separate DynamoDB table (referred to as the "statistics table") for easy access and retrieval.

5. **GetDataStack**:
   - The `GetDataStack` is a CDK stack responsible for deploying the Lambda function that handles data retrieval and sets up API Gateway endpoints.
   - The Lambda function processes API requests for retrieving match details, match statistics, and team statistics.
   - Depending on the endpoint requested, the Lambda function fetches the relevant data from the DynamoDB table and/or the statistics table and returns the appropriate response in JSON format.

6. **API Gateway**:
   - The API Gateway acts as the entry point for external requests to interact with the application.
   - It provides the endpoints for data ingestion (POST /ingest) and data retrieval (GET /matches, GET /matches/{match_id}, GET /matches/{match_id}/statistics, GET /teams/{team_name}/statistics).

7. **Statistics Table**:
   - The "statistics table" is a separate DynamoDB table used to store calculated statistics and information based on the match events ingested.
   - The data processing Lambda populates this table with statistics like the total number of goals scored by each team, total fouls, etc.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
