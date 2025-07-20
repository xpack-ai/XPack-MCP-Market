# XPack-MCP-Market
![b1](https://github.com/user-attachments/assets/3d50cd9a-9d28-4ec8-bb5f-d3668475b49e)

**XPack** is a lightweight, open-source marketplace framework for MCP (Model Context Protocol) services.  
It allows you to transform any OpenAPI into a monetizable MCP service and build your own API store in just minutes.

- ✅ **One-click OpenAPI → MCP service config**
- 🧾 **Service homepage + pricing model**
- 💳 **Built-in billing (per-call / token-based)**
- 📊 **Call logs and usage analytics**
- 👥 **User account management**
- 🌐 **Multi-tenant ready**
- 🛠 **Support Stripe, Alipay, WeChat Pay**
- 🔐 **Email & Google OAuth Sign in**


🚀You can launch XPack in minutes with this single-line installer:

```bash
curl -sSO https://download.xpack.com/install/quick-start.sh; bash quick-start.sh
```

📘Everything is open-source and licensed under **Apache 2.0** — ready for commercial use.

# 📸 Screenshots
![b2](https://github.com/user-attachments/assets/c8cc89a4-ab5f-4c90-8c97-9207b5c9f5c1)
![b3](https://github.com/user-attachments/assets/16f74c8a-b35e-40a7-8471-a5736de8e904)
![b4](https://github.com/user-attachments/assets/fc76c215-7544-4267-bc6f-22a719edec00)
![b5](https://github.com/user-attachments/assets/db40ea77-58c3-472d-ba94-35dc9716a980)

<img width="1415" height="797" alt="image" src="https://github.com/user-attachments/assets/5f71bfcf-c128-42ab-8077-3f2ede549f80" />

<img width="1415" height="797" alt="image" src="https://github.com/user-attachments/assets/d7c0b40d-182e-47a6-bcdf-bd36970f5ee6" />

<img width="1415" height="797" alt="image" src="https://github.com/user-attachments/assets/ae40f659-87ad-42d4-8379-b47a48eb6a29" />

<img width="1415" height="797" alt="image" src="https://github.com/user-attachments/assets/1049f4e5-ec3f-4520-8480-6d6432d6f5d2" />

## Deployment
**Recommended Hardware**
- CPU: 8 cores
- Memory: 16GB
- Storage: 200GB
- Operating System: Linux
- System Architecture: AMD64

**Minimum Hardware**
- CPU: 2 cores
- Memory: 4GB
- Storage: 200GB
- Operating System: Linux / Mac
- System Architecture: AMD64 / ARM64

**Dependencies**
**XPack-MCP-Market** requires `MySQL, Redis, RabbitMQ` with the following versions:
- **MySQL:** >= 5.7.x
- **Redis:** >= 6.2.x
- **RabbitMQ:** >=4.0
- 
### Quick Start Script
> Supported Systems:
> - CentOS 7.9 (representing 7.x)
> - CentOS 8.5 (representing 8.x)
> - Ubuntu 20.04
> - Ubuntu 22.04
> - Debian 12.4
> - Alibaba Cloud Linux 3.2104
> - Alibaba Cloud Linux 2.1903

If you need one-click deployment for other systems, please submit an [Issue](https://github.com/xpack-ai/XPack-MCP-Market/issues).

```
curl -sSO https://download.xpack.com/install/quick-start.sh; bash quick-start.sh
```

### Docker-Compose Deployment
To install XPack-MCP-Market using this method, you need to have [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/standalone/) installed.
1. Edit the `docker-compose.yml` file
```
vi docker-compose.yml
```
2. Modify the configuration, you can reference the original file at [docker-compose.yml](https://github.com/xpack-ai/XPack-MCP-Market/blob/main/scripts/docker-compose.yml)
```
version: '3'
services:
  xpack-mysql:
    image: mysql:8.0.37
    privileged: true
    restart: always
    container_name: xpack-mysql
    hostname: xpack-mysql
    command:
      - "--character-set-server=utf8mb4"
      - "--collation-server=utf8mb4_unicode_ci"
    ports:
      - "33306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=mysql_ZTdhRB
      - MYSQL_DATABASE=xpack
    volumes:
      - /var/lib/xpack/mysql:/var/lib/mysql
    networks:
      - xpack
  xpack-mcp-market:
    image: xpackai/xpack-mcp-market
    container_name: xpack-mcp-market
    privileged: true
    restart: always
    networks:
      - xpack
    ports:
      - "3000:3000"
    depends_on:
      - xpack-mysql
      - xpack-redis
      - xpack-rabbitmq
  xpack-redis:
    container_name: xpack-redis
    image: redis:7.2.4
    hostname: xpack-redis
    privileged: true
    restart: always
    ports:
      - 6379:6379
    command:
      - bash
      - -c
      - "redis-server --protected-mode yes --logfile redis.log --appendonly no --port 6379 --requirepass redis_6sJZDm"
    networks:
      - xpack
  xpack-rabbitmq:
    image: rabbitmq:4.1.2-alpine
    container_name: xpack-rabbitmq
    privileged: true
    restart: always
    environment:
      - RABBITMQ_DEFAULT_USER=rabbitmq
      - RABBITMQ_DEFAULT_PASS=rabbitmq_Gs123dA
    networks:
      - xpack
networks:
  xpack:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.101.0.0/24
```
3. Start XPack-MCP-Market
```
docker-compose up -d
``` 
4. Access `XPack-MCP-Market` in your browser at port 3000


# 🌍 License
This project is licensed under the Apache 2.0 License.
You are free to use it for commercial or personal projects.
