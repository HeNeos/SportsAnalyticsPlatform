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
        # Get the new item from the DynamoDB event
        for item in event["Records"]:
            new_item = item["dynamodb"]
            if "NewImage" not in new_item.keys():
                continue
            new_item = new_item["NewImage"]

            # Extract required attributes for data processing
            event_type = new_item.get("EventType", {}).get("S")
            event_details = new_item.get("EventDetails", {}).get("S")
            team_name = new_item.get("Team", {}).get("S")
            opponent_team_name = new_item.get("Opponent", {}).get("S")
            match_id = new_item.get("MatchID", {}).get("S")

            if not event_type or not team_name or not match_id or not event_details:
                return

            event_details = json.loads(event_details)
            # Calculate statistics based on the event_type
            if event_type == "goal":
                update_statistics(statistics_table, match_id, team_name, opponent_team_name, "total_goals_scored", 1)
                update_statistics(statistics_table, match_id, opponent_team_name, team_name,"total_goals_conceded", 1)
            elif event_type == "foul":
                update_statistics(statistics_table, match_id, team_name, opponent_team_name, "total_fouls", 1)
                update_statistics(statistics_table, match_id, opponent_team_name, team_name, "total_fouls", 0)

            update_match_result(statistics_table, team_name, opponent_team_name, match_id)

            response = statistics_table.get_item(Key={"TeamName": team_name, "MatchID": match_id}, AttributesToGet=["Date"])
            if "Item" not in response or not response.get("Item", {}):
                date = new_item.get("Timestamp", {}).get("S")
                update_date(statistics_table, team_name, match_id, date)
                update_date(statistics_table, opponent_team_name, match_id, date)


    except Exception as e:
        print(f"Error processing data: {e}")
        raise e

def update_statistics(statistics_table, match_id, team_name, opponent_name, statistic_type, value):
    # Get the existing statistics for the team from the statistics table
    response = statistics_table.get_item(Key={"TeamName": team_name, "MatchID": match_id})

    if "Item" not in response or not response.get("Item", {}):
        # If the team and match are not present in the statistics table, create a new entry
        item = {
            "TeamName": team_name,
            "MatchID": match_id,
            "Opponent": opponent_name,
            statistic_type: str(value)
        }
        statistics_table.put_item(Item=item)
    else:
        # If the team and match are already present in the statistics table, update the existing entry
        existing_item = response["Item"]
        existing_item[statistic_type] = str(int(existing_item.get(statistic_type, "0")) + value)
        statistics_table.put_item(Item=existing_item)

def update_match_result(statistics_table, team_name, opponent_name, match_id):
    response = statistics_table.get_item(Key={"TeamName": team_name, "MatchID": match_id})
    response = response.get("Item", {})
    goals_scored = response.get("total_goals_scored", "0")
    goals_conceded = response.get("total_goals_conceded", "0")

    # Calculate match result based on goals scored and conceded
    results = {
        1: "win",
        -1: "loss",
        0: "draw",
    }
    sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
    result = sign(int(goals_scored) - int(goals_conceded))

    # Update match result for the team
    response = statistics_table.update_item(
        Key={"TeamName": team_name, "MatchID": match_id},
        UpdateExpression="SET #result = :result",
        ExpressionAttributeNames={"#result": "Result"},
        ExpressionAttributeValues={":result": results[result]}
    )

    # Update match result for the opponent team
    response = statistics_table.update_item(
        Key={"TeamName": opponent_name, "MatchID": match_id},
        UpdateExpression="SET #result = :result",
        ExpressionAttributeNames={"#result": "Result"},
        ExpressionAttributeValues={":result": results[-result]}
    )

def update_date(table, team_name, match_id, date):
    # Update the "Date" attribute in the StatisticsTable for the team and match_id
    table.update_item(
        Key={"TeamName": team_name, "MatchID": match_id},
        UpdateExpression="SET #dateAttr = :dateValue",
        ExpressionAttributeNames={"#dateAttr": "Date"},
        ExpressionAttributeValues={":dateValue": str(date)}
    )