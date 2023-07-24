import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambda_event_sources from 'aws-cdk-lib/aws-lambda-event-sources'
import * as path from 'path';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam'

export class DynamoDBStack extends cdk.Stack {
  public readonly dynamoTable: dynamodb.Table;
  public readonly statisticsTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.dynamoTable = new dynamodb.Table(
        this,
        'MetadataTable',
        {
            partitionKey: {
                name: 'MatchID', 
                type: dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: 'Timestamp',
                type: dynamodb.AttributeType.STRING
            },
            stream: dynamodb.StreamViewType.NEW_IMAGE,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        }
    );

    this.statisticsTable = new dynamodb.Table(
        this,
        'StatisticsTable',
        {
            partitionKey: {
                name: 'TeamName',
                type: dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: 'MatchID',
                type: dynamodb.AttributeType.STRING
            },
            removalPolicy: cdk.RemovalPolicy.DESTROY
        }
    )

    const lambdaRole = this.createLambdaRole();

    // Create the Lambda function for data processing
    const dataProcessingLambda = new lambda.Function(this, 'DataProcessingLambda', {
        runtime: lambda.Runtime.PYTHON_3_9,
        handler: 'lambda_function.lambda_handler',
        code: lambda.Code.fromAsset(path.join(path.join('services', 'dynamodb', 'runtime'))),
        role: lambdaRole,
        environment: {
            STATISTICS_TABLE_NAME: this.statisticsTable.tableName
        },
    });

    // Grant the Lambda function read access to the DynamoDB table
    this.dynamoTable.grantReadWriteData(dataProcessingLambda);
    this.statisticsTable.grantReadWriteData(dataProcessingLambda);

    if(this.dynamoTable.tableStreamArn){
        dataProcessingLambda.addEventSource(new lambda_event_sources.DynamoEventSource(
            this.dynamoTable, {
                startingPosition: lambda.StartingPosition.LATEST,
                filters: [
                    lambda.FilterCriteria.filter({eventName: lambda.FilterRule.isEqual('INSERT')}),
                    lambda.FilterCriteria.filter({eventName: lambda.FilterRule.isEqual('MODIFY')})
                ]
            }
        ));
    }
  }

  private createLambdaRole(): iam.Role {
    const role = new iam.Role(this, 'LambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    // Add necessary permissions for the Lambda function to access the DynamoDB table stream if stream is enabled
    if (this.dynamoTable.tableStreamArn) {
      const dynamoDBStreamPolicy = new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['dynamodb:GetRecords', 'dynamodb:GetShardIterator', 'dynamodb:DescribeStream', 'dynamodb:ListStreams'],
        resources: [this.dynamoTable.tableStreamArn],
      });
      role.addToPolicy(dynamoDBStreamPolicy);
    }

    const logsPolicy = new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: ['arn:aws:logs:*:*:*'],
    })
    role.addToPolicy(logsPolicy)

    return role;
  }
}