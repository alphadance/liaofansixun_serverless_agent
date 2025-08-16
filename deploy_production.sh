#!/bin/bash
# Production deployment script using systemd

SERVICE_NAME="liaofansixun-proxy"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="/opt/liaofansixun-proxy"
APP_USER="liaofansixun"

echo "Deploying Liao Fan Si Xun proxy server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false $APP_USER
    echo "Created system user: $APP_USER"
fi

# Create application directory
mkdir -p $APP_DIR
cp -r app.py requirements.txt .env $APP_DIR/
chown -R $APP_USER:$APP_USER $APP_DIR

# Setup virtual environment
cd $APP_DIR
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER venv/bin/pip install -r requirements.txt

# Create systemd service file
cat > $SERVICE_FILE << EOF
[Unit]
Description=Liao Fan Si Xun Proxy Server
After=network.target

[Service]
Type=exec
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/uvicorn app:app --host 0.0.0.0 --port \${PORT:-8000}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Deployment complete!"
echo "Service status: systemctl status $SERVICE_NAME"
echo "View logs: journalctl -u $SERVICE_NAME -f"