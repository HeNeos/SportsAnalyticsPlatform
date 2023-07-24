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

    statistics_table_name = os.environ["STATISTICS_TABLE_NAME"]
    statistics_table = dynamodb.Table(statistics_table_name)
    try:
        # Get the path and match_id from the API Gateway event
        path = event.get("path").split('/')[1:]

        # Check if the match_id is provided
        if len(path) < 2:
            response = {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "Missing match_id parameter.",
                }),
            }
            return response

        match_id = path[1]

        # Retrieve the match details from DynamoDB for the specified match_id
        response = table.query(
            KeyConditionExpression="MatchID = :matchid",
            ExpressionAttributeValues={":matchid": match_id}
        )

        # Check if the match exists in the table
        if "Items" not in response or not response["Items"]:
            response = {
                "statusCode": 404,
                "body": json.dumps({
                    "status": "error",
                    "message": "Match not found.",
                }),
            }
            return response

        # Extract required attributes for the match
        match_data = response.get("Items", [])
        match_team = match_data[0].get("Team")
        match_opponent = match_data[0].get("Opponent")
        match_statistics = statistics_table.get_item(Key={"TeamName": match_team, "MatchID": match_id})
        match_date = match_statistics.get("Item", {}).get("Date")
        match_fouls = match_statistics.get("Item", {}).get("total_fouls", "0")
        goals_scored = int(match_statistics.get("Item", {}).get("total_goals_scored", "0"))
        goals_conceded = int(match_statistics.get("Item", {}).get("total_goals_conceded", "0"))


        if path[-1] == "statistics":
            # Retrieve match statistics for the specific match_id
            # Code for calculating match statistics goes here...

            match_statistics = {
                "team": match_team,
                "opponent": match_opponent,
                "total_goals": str(goals_scored + goals_conceded),
                "total_fouls": match_fouls,
                "ball_possession_percentage": str((1+goals_scored)/(1+goals_conceded)) # More data is needed here.
            }

            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "match_id": match_id,
                    "statistics": match_statistics
                }),
            }
        else:
            # Retrieve the list of events for the match
            events = []
            for item in match_data:
                details = json.loads(item.get("EventDetails", {}))
                player = details.get("player", {})
                event = {
                    "event_type": item.get("EventType"),
                    "timestamp": item.get("Timestamp"),
                    "player": player.get("name", "NaN"),
                    "goal_type": details.get("goal_type", "NaN"),
                    "minute": details.get("minute", "NaN"),
                    "video_url": details.get(
                        "video_url", 
                        f"https://example.com/{details.get('goal_type', 'NaN')}{uuid4()}.mp4"
                    )
                }
                events.append(event)

            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "match": {
                        "match_id": match_id,
                        "team": match_team,
                        "opponent": match_opponent,
                        "date": match_date,
                        "events": events
                    }
                }),
            }

        return response

    except Exception as e:
        # Return an error response if there's any issue with the retrieval
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "Failed to retrieve match details.",
                "error": str(e)
            }),
        }
        return response