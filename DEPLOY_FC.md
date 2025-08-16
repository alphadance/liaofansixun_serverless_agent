# Deploying to Alibaba Cloud Function Compute

This guide explains how to deploy the Liao Fan Si Xun proxy server to Alibaba Cloud Function Compute (FC).

## Prerequisites

1. Alibaba Cloud account with Function Compute service enabled
2. Aliyun CLI or Fun CLI installed (optional, for command-line deployment)
3. DashScope API key
4. Bailian Agent ID

## Deployment Methods

### Method 1: Using Alibaba Cloud Console (Recommended)

1. **Build the deployment package:**
   ```bash
   ./build_fc.sh
   ```
   This creates `fc_deploy.zip` containing all necessary files.

2. **Create Function in Console:**
   - Log in to [Alibaba Cloud Function Compute Console](https://fc.console.aliyun.com)
   - Click "Create Service" → Name it `liaofansixun-service`
   - Click "Create Function" with these settings:
     - Function Name: `liaofansixun-proxy`
     - Runtime: Python 3.9
     - Handler: `index.handler`
     - Memory: 512 MB
     - Timeout: 30 seconds
     - Upload Code: Select `fc_deploy.zip`

3. **Configure Environment Variables:**
   - DASHSCOPE_API_KEY: Your DashScope API key
   - BAILIAN_AGENT_ID: Your Bailian agent ID

4. **Create HTTP Trigger:**
   - Trigger Type: HTTP
   - Authorization: Anonymous (or configure as needed)
   - Request Methods: GET, POST

5. **Test the Function:**
   ```bash
   # Health check
   curl https://your-function-url/health
   
   # Process request
   curl -X POST https://your-function-url/process \
     -H "Content-Type: application/json" \
     -d '{"user_input": "你好"}'
   ```

### Method 2: Using Fun CLI

1. **Install Fun CLI:**
   ```bash
   npm install -g @alicloud/fun
   ```

2. **Configure credentials:**
   ```bash
   fun config
   ```

3. **Deploy using template:**
   ```bash
   # Build package first
   ./build_fc.sh
   
   # Deploy
   fun deploy -t fc_template.yml \
     --parameter DashScopeApiKey=your-api-key \
     --parameter BailianAgentId=your-agent-id
   ```

### Method 3: Using Serverless Devs

1. **Install Serverless Devs:**
   ```bash
   npm install -g @serverless-devs/s
   ```

2. **Create s.yaml:**
   ```yaml
   edition: 1.0.0
   name: liaofansixun
   access: default
   
   services:
     fc-deploy:
       component: fc
       props:
         region: cn-shanghai
         service:
           name: liaofansixun-service
           description: Liao Fan Si Xun Proxy Service
         function:
           name: liaofansixun-proxy
           runtime: python3.9
           codeUri: ./fc_deploy.zip
           handler: index.handler
           memorySize: 512
           timeout: 30
           environmentVariables:
             DASHSCOPE_API_KEY: ${env.DASHSCOPE_API_KEY}
             BAILIAN_AGENT_ID: ${env.BAILIAN_AGENT_ID}
         triggers:
           - name: http-trigger
             type: http
             config:
               authType: anonymous
               methods:
                 - GET
                 - POST
   ```

3. **Deploy:**
   ```bash
   export DASHSCOPE_API_KEY=your-api-key
   export BAILIAN_AGENT_ID=your-agent-id
   s deploy
   ```

## Post-Deployment Configuration

### Custom Domain (Optional)

1. In FC Console, go to "Custom Domains"
2. Add your domain and configure DNS
3. Map routes to your function

### Enable Logging

1. Create Log Service project and logstore
2. Configure function logging in FC Console
3. View logs for debugging

### Set Up Monitoring

1. Enable CloudMonitor for your function
2. Set up alerts for errors or high latency
3. Monitor invocation metrics

## Cost Optimization

- Function Compute charges per request and compute time
- Consider using Reserved Instances for consistent traffic
- Enable auto-scaling based on your needs

## Troubleshooting

1. **Function timeout errors:**
   - Increase timeout in function configuration
   - Check if DashScope API is responding slowly

2. **Authentication errors:**
   - Verify DASHSCOPE_API_KEY is correctly set
   - Check API key permissions

3. **500 errors:**
   - Check function logs in Log Service
   - Verify all dependencies are included in deployment package

## Security Best Practices

1. Use RAM roles instead of hardcoding credentials
2. Enable HTTPS for custom domains
3. Set up API Gateway for advanced authentication
4. Regularly rotate API keys

## Next Steps

- Set up CI/CD pipeline for automated deployments
- Configure API Gateway for rate limiting
- Implement monitoring and alerting
- Add custom domain with SSL certificate