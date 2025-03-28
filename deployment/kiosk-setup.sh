#!/bin/bash
# Revvy AI Companion - Kiosk Mode Setup

echo "Setting up Revvy AI Companion in Kiosk Mode..."

# Create autostart directory if it doesn't exist
mkdir -p /home/pi/.config/autostart

# Create kiosk mode autostart entry
cat > /home/pi/.config/autostart/revvy-kiosk.desktop << EOF
[Desktop Entry]
Type=Application
Name=Revvy AI Companion
Exec=/bin/bash /opt/revvy/scripts/start-kiosk.sh
X-GNOME-Autostart-enabled=true
EOF

# Create kiosk startup script
cat > /opt/revvy/scripts/start-kiosk.sh << EOF
#!/bin/bash

# Wait for the desktop to fully load
sleep 10

# Disable screen blanking and power management
xset s off
xset s noblank
xset -dpms

# Hide the cursor after 0.5 seconds of inactivity
unclutter -idle 0.5 -root &

# Launch Chromium in kiosk mode
chromium-browser --noerrdialogs --kiosk --disable-infobars --no-first-run http://localhost:5000 &

# Start the input trap to prevent escape from kiosk mode
/opt/revvy/scripts/input-trap.sh &
EOF

# Create input trap script to prevent kiosk escape
cat > /opt/revvy/scripts/input-trap.sh << EOF
#!/bin/bash

# Trap keyboard shortcuts that could exit kiosk mode
while true; do
  # Check if chromium is running
  if ! pgrep -x chromium-browser > /dev/null; then
    # Restart kiosk if chromium is closed
    chromium-browser --noerrdialogs --kiosk --disable-infobars http://localhost:5000 &
  fi
  
  # Short sleep to prevent high CPU usage
  sleep 2
done
EOF

# Make scripts executable
chmod +x /opt/revvy/scripts/start-kiosk.sh
chmod +x /opt/revvy/scripts/input-trap.sh

# Modify system settings to prevent normal users from exiting
# Disable Ctrl+Alt+Del
systemctl mask ctrl-alt-del.target

# Disable Alt+F4 in the window manager
echo 'xfconf-query -c xfwm4 -p /general/easy_click -s none' >> /home/pi/.config/autostart/disable-alt-f4.sh
chmod +x /home/pi/.config/autostart/disable-alt-f4.sh

echo "Kiosk mode setup complete. System will start in kiosk mode on next boot."