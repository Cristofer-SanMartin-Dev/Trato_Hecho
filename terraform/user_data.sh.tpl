#!/bin/bash
set -eux

# ── Paquetes base ─────────────────────────────────────────────
dnf update -y
dnf install -y docker git

systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# ── Node.js 20 LTS ────────────────────────────────────────────
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# ── n8n (Docker) ──────────────────────────────────────────────
docker volume create n8n_data

docker run -d \
  --name sanos-n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e N8N_HOST=${webhook_host} \
  -e WEBHOOK_URL=http://${webhook_host}:5678/ \
  -e GENERIC_TIMEZONE=America/Santiago \
  -e TZ=America/Santiago \
  -e N8N_DIAGNOSTICS_ENABLED=false \
  -e N8N_VERSION_NOTIFICATIONS_ENABLED=false \
  -e N8N_SECURE_COOKIE=false \
  -e SUPABASE_URL=${supabase_url} \
  -e SUPABASE_KEY=${supabase_key} \
  -e MERCADOPAGO_ACCESS_TOKEN=${mercadopago_access_token} \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n:latest

# ── Frontend (clona el repo y lo corre como servicio) ────────
cd /home/ec2-user
git clone ${repo_url} app
chown -R ec2-user:ec2-user /home/ec2-user/app

cat > /etc/systemd/system/trato-hecho-frontend.service <<'UNIT'
[Unit]
Description=Trato Hecho Frontend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=5
Environment=PORT=3000
Environment=HOST=0.0.0.0

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable trato-hecho-frontend
systemctl start trato-hecho-frontend
