import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as path from 'path';

export class PostDataStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: cdk.StackProps, dynamoDBTable: dynamodb.Table, statisticsTable: dynamodb.Table) {
    super(scope, id, props);

    // Define the Lambda function that will put data into the DynamoDB table
    const dataIngestionLambda = new lambda.Function(this, 'DataIngestionLambda', {
        runtime: lambda.Runtime.PYTHON_3_9,
        handler: 'lambda_function.lambda_handler',
        code: lambda.Code.fromAsset(path.join('services', 'post_data', 'runtime')),
        maxEventAge: cdk.Duration.minutes(5),
        environment: {
          DYNAMODB_TABLE_NAME: dynamoDBTable.tableName,
        }
    });

    // Grant the Lambda function read/write permissions to the DynamoDB table
    dynamoDBTable.grantReadWriteData(dataIngestionLambda);
    statisticsTable.grantReadWriteData(dataIngestionLambda);

    // Define the API Gateway and create a resource with a POST method
    const api = new apigw.RestApi(this, 'DataIngestionApi');
    const resource = api.root.addResource('ingest');
    const integration = new apigw.LambdaIntegration(dataIngestionLambda);

    // Create the API Gateway method and connect it to the Lambda function integration
    resource.addMethod('POST', integration);

    // Output the API Gateway endpoint URL for testing
    new cdk.CfnOutput(this, 'ApiEndpoint', { value: api.url });
  }
}
