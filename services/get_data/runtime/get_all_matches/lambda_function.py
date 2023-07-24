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
        # Retrieve all matches from DynamoDB
        response = statistics_table.scan()

        if "Items" not in response or not response["Items"]:
            # If no matches found in the table, return an empty response
            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "matches": []
                }),
            }
        else:
            # Extract matches and their statistics from the response
            matches = response["Items"]
            matches_response = []
            set_id = set()

            for match in matches:
                match_id = match["MatchID"]

                if match_id in set_id:
                    continue
                else:
                    set_id.add(match_id)
                
                team_name = match["TeamName"]
                opponent = match.get("Opponent", "")  # If 'Opponent' key is not present, set it to an empty string
                date = match.get("Date", "")  # If 'Date' key is not present, set it to an empty string

                # Extract match statistics from the item
                total_goals_scored = match.get("total_goals_scored", 0)
                total_goals_conceded = match.get("total_goals_conceded", 0)

                # Assemble the match details and statistics for the response
                match_response = {
                    "match_id": match_id,
                    "team": team_name,
                    "opponent": opponent,
                    "date": date,
                    "statistics": {
                        "total_goals_scored": total_goals_scored,
                        "total_goals_conceded": total_goals_conceded,
                    }
                }

                matches_response.append(match_response)

            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "matches": matches_response
                }),
            }

        return response

    except Exception as e:
        # Return an error response if there's any issue with the retrieval
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "Failed to retrieve matches.",
                "error": str(e)
            }),
        }
        return response
