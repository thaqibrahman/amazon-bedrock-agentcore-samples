
import boto3
import json
import logging
from boto3.session import Session
from botocore.exceptions import ClientError

boto_session = Session()
region = boto_session.region_name
client = boto3.client('bedrock-agentcore', region_name=region)

ssm_client = boto3.client("ssm", region_name=region)
agent_arn_response = ssm_client.get_parameter(Name="/mcp_server/runtime_iam/agent_arn")
runtime_arn = agent_arn_response["Parameter"]["Value"]

def call_mcp(method, params=None):
    if params is None:
        params = {}
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }).encode()
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            payload=payload,
            qualifier='DEFAULT',
            contentType='application/json',
            accept='application/json, text/event-stream'
        )
        raw = response['response'].read().decode()
        json_data = json.loads(raw[raw.find('{'):])
        return json_data['result']
    except ClientError as e:
        print(f"❌ Error: {e}")
        raise

def main():
    
    print(f"Using AWS region: {region}")
    print(f"Retrieved Agent ARN: {runtime_arn}")


    print("\n🔄 Listing available tools...")
    try: 
        tools_result = call_mcp("tools/list")

        print("\n📋 Available MCP Tools:")
        print("=" * 50)
        for tool in tools_result['tools']:
            print(f"🔧 {tool['name']}: {tool['description']}")

        print("\n🧪 Testing MCP Tools:")
        print("=" * 50)

        print("\n➕ Testing add_numbers(5, 3)...")
        add_result = call_mcp("tools/call", {"name": "add_numbers", "arguments": {"a": 5, "b": 3}})
        print(f"   Result: {add_result['structuredContent']}")

        print("\n✖️  Testing multiply_numbers(4, 7)...")
        multiply_result = call_mcp("tools/call", {"name": "multiply_numbers", "arguments": {"a": 4, "b": 7}})
        print(f"   Result: {multiply_result['structuredContent']}")

        print("\n👋 Testing greet_user('Alice')...")
        greet_result = call_mcp("tools/call", {"name": "greet_user", "arguments": {"name": "Alice"}})
        print(f"   Result: {greet_result['structuredContent']}")

        print("\n✅ MCP tool testing completed!")

    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        import traceback

        print("\n🔍 Full error traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
