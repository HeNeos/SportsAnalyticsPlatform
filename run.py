import subprocess
import os
import json

stack_prefix_name = ""

print(f"\U0001F6A7 Creating virtual python environment...\n")
try:
    e = subprocess.run(["python3", "-m", "venv", ".venv"], check=True)
except:
    EnvironmentError("Failed to create a virtual python environment")
print(f"\U00002705 Successfully created virtual python environment\n")

os.system("source .venv/bin/activate")

print(f"\U0001F6A7 Installing requirements/packages/dependencies ...\n")
try:
    e = subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
except:
    raise EnvironmentError("Failed to install 'requirements.txt' in the virtual python environment")

print(f"\U0001F680 Starting deployment\n")
try:
    e = subprocess.run(["cdk",  "synth"], check=True)
except:
    raise Exception("Failed to run 'cdk synth'")
print(f"\U00002705 Successfully run 'cdk synth'\n")

print(f"\U0001F680 Deploying 'DynamoDBStack'\n")
try:
    e = subprocess.run(["cdk", "deploy", f"{stack_prefix_name}DynamoDBStack", "--require-approval", "never"], check=True)
except:
    raise Exception("Failed to deploy stack: DynamoDBStack")
print(f"\U00002705 Successfully deployed 'DynamoDBStack'\n")

print(f"\U0001F680 Deploying 'TestPostDataStack'\n")
try:
    e = subprocess.run(["cdk", "deploy", f"{stack_prefix_name}PostDataStack", "--require-approval", "never"], check=True)
except:
    raise Exception("Failed to deploy stack: PostDataStack")
print(f"\U00002705 Successfully deployed 'PostDataStack'\n")

print(f"\U0001F680 Deploying 'GetDataStack'\n")
try:
    e = subprocess.run(["cdk", "deploy", f"{stack_prefix_name}GetDataStack", "--require-approval", "never"], check=True)
except:
    raise Exception("Failed to deploy stack: GetDataStack")
print(f"\U00002705 Successfully deployed 'GetDataStack'\n")


print(f"\U00002705 Deployment completed\n")