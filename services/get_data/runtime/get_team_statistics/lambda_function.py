import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    logger.info(f"EVENT: {event}")

    statistics_table_name = os.environ["STATISTICS_TABLE_NAME"]
    statistics_table = dynamodb.Table(statistics_table_name)
    try:
        # Get the team_name from the API Gateway path parameters
        team_name = event.get("pathParameters", {}).get("team_name")

        # Check if the team_name is provided
        if not team_name:
            response = {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "Missing team_name parameter.",
                }),
            }
            return response

        # Retrieve team statistics from the StatisticsTable
        response = statistics_table.query(
            KeyConditionExpression="TeamName = :team",
            ExpressionAttributeValues={":team": team_name}
        )

        if "Items" not in response or not response["Items"]:
            # If team statistics not found in the table, return an error response
            response = {
                "statusCode": 404,
                "body": json.dumps({
                    "status": "error",
                    "message": "Team statistics not found.",
                }),
            }
            return response

        # Extract team statistics from the response
        team_statistics = response["Items"]

        # Calculate total_matches
        total_matches = len(team_statistics)

        # Calculate total_wins, total_draws, and total_losses
        total_wins = sum(1 for item in team_statistics if item.get("Result") == "win")
        total_draws = sum(1 for item in team_statistics if item.get("Result") == "draw")
        total_losses = sum(1 for item in team_statistics if item.get("Result") == "loss")

        # Calculate total_goals_scored and total_goals_conceded
        total_goals_scored = sum(int(item.get("total_goals_scored", 0)) for item in team_statistics)
        total_goals_conceded = sum(int(item.get("total_goals_conceded", 0)) for item in team_statistics)

        response = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "team": team_name,
                "statistics": {
                    "total_matches": total_matches,
                    "total_wins": total_wins,
                    "total_draws": total_draws,
                    "total_losses": total_losses,
                    "total_goals_scored": total_goals_scored,
                    "total_goals_conceded": total_goals_conceded,
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
                "message": "Failed to retrieve team statistics.",
                "error": str(e)
            }),
        }
        return response
