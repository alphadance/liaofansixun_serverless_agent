# Liaofansixun Serverless Agent

A serverless FastAPI proxy for the Liao Fan Si Xun (了凡四训) Cultivation Assistant on Alibaba Cloud Bailian platform.

## Features

- 🚀 Serverless deployment on Alibaba Cloud Function Compute
- 🤖 Integration with DashScope API for AI agent capabilities
- 💬 Session management for continuous conversations
- ⚡ Auto-scaling and high availability
- 🔒 Secure API key management

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/alphadance/liaofansixun_serverless_agent.git
cd liaofansixun_serverless_agent
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API credentials
./setup.sh
```

3. Run locally:
```bash
./start.sh
```

### Deployment to Alibaba Cloud Function Compute

```bash
# Set credentials
export DASHSCOPE_API_KEY=your-api-key
export BAILIAN_AGENT_ID=your-agent-id

# Deploy
./deploy_fc.sh
```

## API Usage

### Health Check
```bash
GET /health
```

### Process User Input
```bash
POST /process
{
    "user_input": "你好，请介绍一下《了凡四训》",
    "session_id": "optional-session-id"
}
```

Response:
```json
{
    "text": "《了凡四训》是明代袁了凡...",
    "session_id": "auto-generated-or-provided-session-id",
    "request_id": "unique-request-id"
}
```

## Project Structure

```
├── app_dashscope.py      # FastAPI server with DashScope
├── fc_index.py          # Function Compute handler
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── build_fc.sh          # Build deployment package
├── deploy_fc.sh         # Deploy to Function Compute
├── fc_template.yml      # Function Compute template
├── s.yaml               # Serverless Devs config
├── setup.sh             # Local development setup
└── start.sh             # Local development server
```

## Environment Variables

- `DASHSCOPE_API_KEY`: Your DashScope API key (required)
- `BAILIAN_AGENT_ID`: Your Bailian agent ID (required)
- `PORT`: Server port for local development (default: 8000)

## About Liao Fan Si Xun (了凡四训)

This agent provides guidance based on "Liao Fan's Four Lessons", a classical Chinese text about:
- 立命之学 (Learning to Create Destiny)
- 改过之法 (Methods of Correcting Faults)
- 积善之方 (Ways of Accumulating Good Deeds)
- 谦德之效 (Benefits of Humility)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.