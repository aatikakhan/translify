# AWS Deployment Guide (Student Account)

This guide deploys Translify on AWS using EC2 + S3 + RDS.

## 1) Create AWS Resources

### A. S3 Bucket
- Create bucket (example: `translify-files-bucket`)
- Keep private access
- Create folders:
  - `originals/`
  - `translated/`

### B. RDS Instance
- Engine: MySQL (or PostgreSQL)
- DB name: `translify`
- Note endpoint, username, password, and port
- Allow inbound from EC2 security group

### C. EC2 Instance
- Ubuntu 22.04
- Open inbound:
  - `22` (SSH)
  - `80` (HTTP)
- Attach IAM role with S3 permissions (recommended)

## 2) Connect and Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx
```

Upload project to EC2 (git clone or copy zip), then:

```bash
cd translify
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Configure Environment

```bash
cp .env.example .env
```

Update `.env`:

- `APP_ENV=production`
- `APP_DEBUG=false`
- `SECRET_KEY=<strong-secret>`
- `USE_LOCAL_STORAGE=false`
- `AWS_REGION=<your-region>`
- `AWS_S3_BUCKET=<your-bucket>`
- `GEMINI_API_KEY=<your-key>`
- `DATABASE_URL=mysql+pymysql://<user>:<pass>@<rds-endpoint>:3306/translify`

If EC2 has IAM role for S3 access, keep AWS access key fields empty.

## 4) Run with Uvicorn (Quick Check)

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://<ec2-public-ip>:8000`

## 5) Configure Systemd Service

Create `/etc/systemd/system/translify.service`:

```ini
[Unit]
Description=Translify FastAPI App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/translify
Environment="PATH=/home/ubuntu/translify/.venv/bin"
ExecStart=/home/ubuntu/translify/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable translify
sudo systemctl start translify
sudo systemctl status translify
```

## 6) Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/translify`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable config:

```bash
sudo ln -s /etc/nginx/sites-available/translify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Open `http://<ec2-public-ip>`

## 7) Evaluation Readiness

- Prepare one non-English PDF
- Keep AWS console tabs ready for S3 and RDS
- Demonstrate full flow:
  - upload -> process -> download
  - show S3 objects
  - show DB metadata entries
