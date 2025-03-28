#!/bin/bash
# Revvy AI Companion - Installation Script

# Display banner
echo "====================================="
echo "  Revvy AI Companion Installation"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi

# Create log directory
mkdir -p /var/log/revvy
touch /var/log/revvy/install.log
exec > >(tee -a /var/log/revvy/install.log) 2>&1

echo "Starting installation at $(date)"
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "Installing system dependencies..."
apt-get install -y \
  python3 python3-pip python3-venv \
  nodejs npm \
  portaudio19-dev libsndfile1 \
  libatlas-base-dev \
  espeak alsa-utils \
  cmake build-essential git

# Create application directory
echo "Setting up application directory..."
mkdir -p /opt/revvy
cd /opt/revvy

# Clone repository if not already downloaded
if [ ! -d "/opt/revvy/revvy-ai-companion" ]; then
  echo "Downloading Revvy AI Companion..."
  git clone https://github.com/TheRealRevvy/revvy-ai-companion.git .
else
  echo "Repository already exists, skipping download."
  cd /opt/revvy/revvy-ai-companion
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install \
  numpy \
  sounddevice \
  soundfile \
  pvporcupine \
  pvrecorder \
  pyttsx3 \
  SpeechRecognition \
  obd \
  llama-cpp-python \
  websockets \
  aiohttp \
  aiohttp_cors

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
npm run build

# Create service file
echo "Creating systemd service..."
cat > /etc/systemd/system/revvy.service << EOF
[Unit]
Description=Revvy AI Companion
After=network.target bluetooth.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/revvy
ExecStart=/opt/revvy/venv/bin/python3 backend/main.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Enable auto-start
echo "Enabling service..."
systemctl daemon-reload
systemctl enable revvy.service

# Create Bluetooth auto-connection script for OBD adapter
echo "Setting up Bluetooth OBD auto-connection..."
cat > /opt/revvy/scripts/obd_connect.sh << EOF
#!/bin/bash
# OBD Bluetooth Connection Script

# OBD device MAC address (set during setup)
OBD_MAC="00:00:00:00:00:00"

# Connect to OBD device
echo "Connecting to OBD device \$OBD_MAC..."
rfcomm bind 0 \$OBD_MAC
EOF

chmod +x /opt/revvy/scripts/obd_connect.sh

# Add script to startup
cat > /etc/systemd/system/revvy-obd-connect.service << EOF
[Unit]
Description=Revvy OBD Connection
After=bluetooth.target
Before=revvy.service

[Service]
Type=oneshot
ExecStart=/opt/revvy/scripts/obd_connect.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable revvy-obd-connect.service

# Download AI model (if not already present)
if [ ! -f "/opt/revvy/ai/models/mistral-7b-instruct-q4_k_m.gguf" ]; then
  echo "Downloading Mistral-7B AI model (this may take a while)..."
  mkdir -p /opt/revvy/ai/models
  curl -L https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -o /opt/revvy/ai/models/mistral-7b-instruct-q4_k_m.gguf
fi

echo "Installation complete!"
echo "Run the setup wizard to configure your OBD connection:"
echo "  sudo python3 /opt/revvy/backend/setup.py"
echo ""
echo "Then start the service:"
echo "  sudo systemctl start revvy"
echo ""
echo "Installation finished at $(date)"