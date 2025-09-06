#!/bin/bash

# OpenFlux Deployment Script for AWS EC2
# This script sets up OpenFlux on an EC2 instance

set -e

echo "🚀 Starting OpenFlux deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-pip python3.11-venv

# Install system dependencies
echo "📋 Installing system dependencies..."
sudo apt-get install -y git curl wget unzip

# Install AWS CLI v2
echo "☁️ Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Install uv (Python package manager)
echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/openflux
sudo chown $USER:$USER /opt/openflux
cd /opt/openflux

# Clone or copy application files (assuming files are already present)
echo "📋 Setting up application files..."

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your configuration:"
    echo "- Set GITHUB_TOKEN"
    echo "- Configure AWS_PROFILE or AWS credentials"
    echo "- Adjust AWS_REGION if needed"
fi

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/openflux.service > /dev/null <<EOF
[Unit]
Description=OpenFlux - MCP Integration Platform
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/openflux
Environment=PATH=/opt/openflux/venv/bin
ExecStart=/opt/openflux/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration (optional)
echo "🌐 Setting up nginx reverse proxy..."
sudo apt-get install -y nginx

sudo tee /etc/nginx/sites-available/openflux > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/openflux /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Start and enable OpenFlux service
echo "🚀 Starting OpenFlux service..."
sudo systemctl daemon-reload
sudo systemctl enable openflux
sudo systemctl start openflux

# Create log directory
sudo mkdir -p /var/log/openflux
sudo chown $USER:$USER /var/log/openflux

echo "✅ OpenFlux deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/openflux/.env with your configuration"
echo "2. Configure AWS credentials: aws configure"
echo "3. Set your GitHub token in the .env file"
echo "4. Restart the service: sudo systemctl restart openflux"
echo "5. Check service status: sudo systemctl status openflux"
echo "6. View logs: sudo journalctl -u openflux -f"
echo ""
echo "🌐 Access OpenFlux at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "🔧 Useful commands:"
echo "- Check service status: sudo systemctl status openflux"
echo "- View logs: sudo journalctl -u openflux -f"
echo "- Restart service: sudo systemctl restart openflux"
echo "- Update application: cd /opt/openflux && git pull && sudo systemctl restart openflux"