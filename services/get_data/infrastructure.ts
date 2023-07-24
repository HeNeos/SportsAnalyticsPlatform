import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as path from 'path';

export class GetDataStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: cdk.StackProps, dynamoDBTable: dynamodb.Table, statisticsTable: dynamodb.Table) {
    super(scope, id, props);

    // Lambda function for /matches endpoint
    const getAllMatchesLambda = new lambda.Function(this, 'GetAllMatchesLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join('services', 'get_data', 'runtime', 'get_all_matches')), 
      environment: {
        DYNAMODB_TABLE_NAME: dynamoDBTable.tableName,
        STATISTICS_TABLE_NAME: statisticsTable.tableName
      },
    });

    // Lambda function for /matches/{match_id} endpoint
    const getMatchDetailsLambda = new lambda.Function(this, 'GetMatchDetailsLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join('services', 'get_data', 'runtime', 'get_match_details')),
      environment: {
        DYNAMODB_TABLE_NAME: dynamoDBTable.tableName,
        STATISTICS_TABLE_NAME: statisticsTable.tableName
      },
    });

    // Lambda function for /teams/{team_name}/statistics endpoint
    const getTeamStatisticsLambda = new lambda.Function(this, 'GetTeamStatisticsLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join('services', 'get_data', 'runtime', 'get_team_statistics')),
      environment: {
        DYNAMODB_TABLE_NAME: dynamoDBTable.tableName,
        STATISTICS_TABLE_NAME: statisticsTable.tableName
      },
    });

    // Grant read permissions to the Lambda functions to access the DynamoDB table
    dynamoDBTable.grantReadData(getAllMatchesLambda);
    dynamoDBTable.grantReadData(getMatchDetailsLambda);
    dynamoDBTable.grantReadData(getTeamStatisticsLambda);

    statisticsTable.grantReadData(getAllMatchesLambda);
    statisticsTable.grantReadData(getMatchDetailsLambda);
    statisticsTable.grantReadData(getTeamStatisticsLambda);

    // API Gateway
    const api = new apigw.RestApi(this, 'GetDataApi');

    // API Gateway Integration for /matches endpoint
    const getAllMatchesIntegration = new apigw.LambdaIntegration(getAllMatchesLambda);
    api.root.addMethod('GET', getAllMatchesIntegration);

    // API Gateway Integration for /matches/{match_id} endpoint
    const getMatchDetailsIntegration = new apigw.LambdaIntegration(getMatchDetailsLambda);
    api.root.addResource('matches').addResource('{match_id}').addMethod('GET', getMatchDetailsIntegration);

    // API Gateway Integration for /teams/{team_name}/statistics endpoint
    const getTeamStatisticsIntegration = new apigw.LambdaIntegration(getTeamStatisticsLambda);
    api.root.addResource('teams').addResource('{team_name}').addResource('statistics').addMethod('GET', getTeamStatisticsIntegration);

    // Output the API Gateway endpoint URL for testing
    new cdk.CfnOutput(this, 'ApiEndpoint', { value: api.url });
  }
}
