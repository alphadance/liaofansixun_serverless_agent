# Deploying to Alibaba Cloud Function Compute

## Prerequisites

1. [Serverless Devs CLI](https://www.serverless-devs.com/serverless-devs/install) installed
2. Alibaba Cloud account configured (`s config add`)
3. DashScope API key and Bailian Agent ID

## Quick Deploy

```bash
# Set credentials
export DASHSCOPE_API_KEY=your-api-key
export BAILIAN_AGENT_ID=your-agent-id

# Deploy
./deploy_fc.sh
```

## Manual Deployment

1. **Build package:**
   ```bash
   ./build_fc.sh
   ```

2. **Deploy with Serverless Devs:**
   ```bash
   s deploy
   ```

## Configuration

The deployment uses these settings (configured in `s.yaml`):
- Runtime: Python 3.12
- Memory: 512 MB
- Timeout: 30 seconds
- Region: cn-hangzhou (change in s.yaml if needed)

## Testing

After deployment, test your function:

```bash
# Get function URL from deployment output
FUNCTION_URL="https://your-function-url"

# Health check
curl $FUNCTION_URL/health

# Process request
curl -X POST $FUNCTION_URL/process \
  -H "Content-Type: application/json" \
  -d '{"user_input": "你好"}'
```

## Troubleshooting

- **Authentication errors**: Verify DASHSCOPE_API_KEY is correctly set
- **Timeout errors**: Increase timeout in s.yaml if needed
- **500 errors**: Check function logs in Alibaba Cloud console