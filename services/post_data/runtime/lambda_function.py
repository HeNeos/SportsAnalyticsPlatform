import json
import os
import boto3
import logging
from uuid import uuid4

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    logger.info(f"EVENT: {event}")
    table_name = os.environ["DYNAMODB_TABLE_NAME"]
    table = dynamodb.Table(table_name)
    try:
        # Parse the incoming event data
        data = json.loads(event["body"])
        # Extract required attributes from the data
        match_id = data.get("match_id")
        timestamp = data.get("timestamp")

        if not match_id:
            raise ValueError("Invalid match_id.")

        team = data.get("team")
        opponent = data.get("opponent")
        event_type = data.get("event_type")
        event_details = data.get("event_details")
        # Store the data in DynamoDB
        table = dynamodb.Table(table_name)
        item_id = f"{match_id}_{timestamp}_{uuid4()}"  # Create a unique item_id using match_id and timestamp
        
        table.put_item(
            Item={
                "MatchID": match_id,
                "Timestamp": timestamp,
                "Team": team,
                "Opponent": opponent,
                "EventType": event_type,
                "EventDetails": json.dumps(event_details)
            }
        )

        # Return a success response
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": "Data successfully ingested.",
                "data": {
                    "event_id": item_id,
                    "timestamp": timestamp
                }
            }),
        }
        return response

    except Exception as e:
        # Return an error response if there's any issue with the ingestion
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "Failed to ingest data.",
                "error": str(e)
            }),
        }
        return response