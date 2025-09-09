# Deployment Guide

## Overview

This guide covers deploying the Vampires Bot in various environments using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Domain name (for production with webhooks)

## Environment Setup

### 1. Development Environment

#### Local Development with Docker

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd vampires_bot
   git checkout feature/docker-postgresql-setup
   ```

2. **Configure environment**:
   ```bash
   cp .env.docker .env
   # Edit .env with your bot token
   nano .env
   ```

3. **Start services**:
   ```bash
   ./start-docker.sh
   ```

4. **Monitor logs**:
   ```bash
   docker-compose logs -f bot
   ```

#### Local Development without Docker

1. **Setup Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup database**:
   ```bash
   # Install PostgreSQL locally or use Docker for DB only
   docker run -d --name postgres -e POSTGRES_DB=vampires_bot -e POSTGRES_USER=bot_user -e POSTGRES_PASSWORD=bot_password -p 5432:5432 postgres:15-alpine
   ```

3. **Run migrations**:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://bot_user:bot_password@localhost:5432/vampires_bot"
   alembic upgrade head
   ```

4. **Start bot**:
   ```bash
   python app.py
   ```

### 2. Staging Environment

#### Docker Compose Deployment

1. **Server setup**:
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy application**:
   ```bash
   git clone <repository>
   cd vampires_bot
   git checkout feature/docker-postgresql-setup
   
   # Configure environment
   cp .env.docker .env
   # Edit .env with staging configuration
   
   # Start services
   docker-compose up -d
   ```

3. **Setup monitoring**:
   ```bash
   # Install monitoring tools
   docker run -d --name prometheus -p 9090:9090 prom/prometheus
   docker run -d --name grafana -p 3000:3000 grafana/grafana
   ```

### 3. Production Environment

#### Production Docker Compose

1. **Security hardening**:
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   services:
     postgres:
       environment:
         POSTGRES_PASSWORD_FILE: /run/secrets/db_password
       secrets:
         - db_password
       # Remove port exposure
       ports: []
     
     bot:
       environment:
         BOT_TOKEN_FILE: /run/secrets/bot_token
       secrets:
         - bot_token
       restart: always
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'
   
   secrets:
     bot_token:
       external: true
     db_password:
       external: true
   ```

2. **Create secrets**:
   ```bash
   echo "your_bot_token" | docker secret create bot_token -
   echo "secure_db_password" | docker secret create db_password -
   ```

3. **Deploy with secrets**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

#### Kubernetes Deployment

1. **Create namespace**:
   ```yaml
   # k8s/namespace.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: vampires-bot
   ```

2. **Create ConfigMap**:
   ```yaml
   # k8s/configmap.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: bot-config
     namespace: vampires-bot
   data:
     LOG_LEVEL: "INFO"
     DEFAULT_LOCALIZATION: "ru"
     TEMPLATE_ROOT: "templates"
     BOT_NAME: "Vampires Bot"
   ```

3. **Create Secret**:
   ```yaml
   # k8s/secret.yaml
   apiVersion: v1
   kind: Secret
     metadata:
       name: bot-secrets
       namespace: vampires-bot
   type: Opaque
   data:
     BOT_TOKEN: <base64-encoded-token>
     DATABASE_URL: <base64-encoded-db-url>
   ```

4. **Create PostgreSQL deployment**:
   ```yaml
   # k8s/postgres.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: postgres
     namespace: vampires-bot
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: postgres
     template:
       metadata:
         labels:
           app: postgres
       spec:
         containers:
         - name: postgres
           image: postgres:15-alpine
           env:
           - name: POSTGRES_DB
             value: vampires_bot
           - name: POSTGRES_USER
             value: bot_user
           - name: POSTGRES_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: bot-secrets
                 key: DATABASE_URL
           ports:
           - containerPort: 5432
           volumeMounts:
           - name: postgres-storage
             mountPath: /var/lib/postgresql/data
         volumes:
         - name: postgres-storage
           persistentVolumeClaim:
             claimName: postgres-pvc
   ```

5. **Create bot deployment**:
   ```yaml
   # k8s/bot.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: bot
     namespace: vampires-bot
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: bot
     template:
       metadata:
         labels:
           app: bot
       spec:
         containers:
         - name: bot
           image: vampires-bot:latest
           envFrom:
           - configMapRef:
               name: bot-config
           - secretRef:
               name: bot-secrets
           resources:
             limits:
               memory: "512Mi"
               cpu: "500m"
             requests:
               memory: "256Mi"
               cpu: "250m"
           livenessProbe:
             exec:
               command:
               - python
               - -c
               - "import sys; sys.exit(0)"
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             exec:
               command:
               - python
               - -c
               - "import sys; sys.exit(0)"
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `DATABASE_URL` | Database connection string | `postgresql+asyncpg://user:pass@host:5432/db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_LOCALIZATION` | Default language | `ru` |
| `TEMPLATE_ROOT` | Template directory | `templates` |
| `BOT_NAME` | Bot display name | `Vampires Bot` |

## Database Management

### Migrations

1. **Create migration**:
   ```bash
   docker-compose exec bot alembic revision --autogenerate -m "Description"
   ```

2. **Apply migration**:
   ```bash
   docker-compose exec bot alembic upgrade head
   ```

3. **Rollback migration**:
   ```bash
   docker-compose exec bot alembic downgrade -1
   ```

### Backup and Restore

1. **Backup database**:
   ```bash
   docker-compose exec postgres pg_dump -U bot_user vampires_bot > backup.sql
   ```

2. **Restore database**:
   ```bash
   docker-compose exec -T postgres psql -U bot_user vampires_bot < backup.sql
   ```

## Monitoring and Logging

### Log Management

1. **View logs**:
   ```bash
   docker-compose logs -f bot
   docker-compose logs -f postgres
   ```

2. **Log rotation**:
   ```yaml
   # Add to docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

### Health Checks

1. **Check service status**:
   ```bash
   docker-compose ps
   ```

2. **Check bot health**:
   ```bash
   docker-compose exec bot python -c "import sys; sys.exit(0)"
   ```

3. **Check database health**:
   ```bash
   docker-compose exec postgres pg_isready -U bot_user -d vampires_bot
   ```

## Security Considerations

### Production Security

1. **Use secrets management**:
   - Docker secrets
   - Kubernetes secrets
   - External secret management systems

2. **Network security**:
   - Don't expose database ports
   - Use internal networks
   - Implement firewall rules

3. **Container security**:
   - Use non-root users
   - Regular security updates
   - Minimal base images

### SSL/TLS Configuration

1. **For webhook mode**:
   ```bash
   # Generate SSL certificate
   certbot certonly --standalone -d yourdomain.com
   
   # Configure nginx
   server {
       listen 443 ssl;
       server_name yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       
       location /webhook {
           proxy_pass http://bot:8000;
       }
   }
   ```

## Scaling Considerations

### Horizontal Scaling

1. **Multiple bot instances**:
   ```yaml
   # docker-compose.yml
   services:
     bot:
       deploy:
         replicas: 3
   ```

2. **Load balancing**:
   - Use nginx or traefik
   - Session affinity not required (stateless)

### Database Scaling

1. **Read replicas**:
   ```yaml
   postgres-read:
     image: postgres:15-alpine
     environment:
       POSTGRES_DB: vampires_bot
     command: postgres -c hot_standby=on
   ```

2. **Connection pooling**:
   ```python
   # In db/session.py
   engine = create_async_engine(
       url,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   ```bash
   # Check logs
   docker-compose logs bot
   
   # Check token
   docker-compose exec bot env | grep BOT_TOKEN
   ```

2. **Database connection failed**:
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Test connection
   docker-compose exec bot python -c "from db.config import load_db_config; print(load_db_config().url)"
   ```

3. **Migration failed**:
   ```bash
   # Check migration status
   docker-compose exec bot alembic current
   
   # Check migration files
   docker-compose exec bot ls -la alembic/versions/
   ```

### Performance Issues

1. **High memory usage**:
   ```bash
   # Check container stats
   docker stats
   
   # Adjust memory limits
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 1G
   ```

2. **Slow database queries**:
   ```bash
   # Check database performance
   docker-compose exec postgres psql -U bot_user -d vampires_bot -c "SELECT * FROM pg_stat_activity;"
   ```

## Maintenance

### Regular Tasks

1. **Update dependencies**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Database maintenance**:
   ```bash
   docker-compose exec postgres psql -U bot_user -d vampires_bot -c "VACUUM ANALYZE;"
   ```

3. **Log cleanup**:
   ```bash
   docker system prune -f
   ```

### Backup Strategy

1. **Automated backups**:
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker-compose exec postgres pg_dump -U bot_user vampires_bot > "backup_${DATE}.sql"
   ```

2. **Backup retention**:
   - Keep daily backups for 30 days
   - Keep weekly backups for 12 weeks
   - Keep monthly backups for 12 months
