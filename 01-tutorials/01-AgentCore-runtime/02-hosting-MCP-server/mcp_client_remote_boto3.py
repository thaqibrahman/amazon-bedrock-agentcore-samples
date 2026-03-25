
import boto3
import json
import traceback
from boto3.session import Session
from botocore.exceptions import ClientError

boto_session = Session()
region = boto_session.region_name
print(f"Using AWS region: {region}")

# Initialize the Bedrock AgentCore and SSM client
client = boto3.client('bedrock-agentcore', region_name=region)
ssm_client = boto3.client("ssm", region_name=region)


agent_arn_response = ssm_client.get_parameter(
        Name="/mcp_server/runtime_iam/agent_arn"
)

runtime_arn = agent_arn_response["Parameter"]["Value"]

print(f"Retrieved Agent ARN: {runtime_arn}")

if not runtime_arn:
        print("❌ Error: AGENT_ARN not found")
        sys.exit(1)
        
def call_mcp(method, params=None):
    """
    Call an MCP method on the agent runtime.
    
    Args:
        method: The MCP method to call (e.g., 'tools/list', 'tools/call')
        params: Optional parameters for the method
    
    Returns:
        The result from the MCP response
    """
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
        print(f"\n{'=' * 60}")
        print("Error Response:")
        print(json.dumps(e.response, indent=2, default=str))
        print(f"{'=' * 60}\n")
        raise


def main():

    try:
        # List available tools
        print("📋 Available MCP Tools:")
        print("=" * 50)
        
        tools_result = call_mcp("tools/list")
        tools = tools_result['tools']
        
        for tool in tools:
            params = list(tool.get('inputSchema', {}).get('properties', {}).keys())
            print(f"🔧 {tool['name']}")
            print(f"   Description: {tool['description']}")
            print(f"   Parameters: {params}")
            print()
        
        print(f"✅ Successfully connected to MCP server!")
        print(f"Found {len(tools)} tools available.")

    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        import traceback

        print("\n🔍 Full error traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
