import * as path from 'path';
import * as cdk from 'aws-cdk-lib';

import {DynamoDBStack} from './services/dynamodb/infrastructure';
import {PostDataStack} from './services/post_data/infrastructure';
import {GetDataStack} from './services/get_data/infrastructure';


const workflow_app = new cdk.App();

const stackPrefixName = ''

const env_usa: cdk.Environment = {
    account: 'AWS_ACCOUNT_ID',
    region: 'us-east-1'
};

const dynamoDBStack = new DynamoDBStack(workflow_app, `${stackPrefixName}DynamoDBStack`, {env: env_usa});
new PostDataStack(workflow_app, `${stackPrefixName}PostDataStack`, { env: env_usa }, dynamoDBStack.dynamoTable, dynamoDBStack.statisticsTable);
new GetDataStack(workflow_app, `${stackPrefixName}GetDataStack`, { env: env_usa }, dynamoDBStack.dynamoTable, dynamoDBStack.statisticsTable);

workflow_app.synth();
