# Docker Volume 使用方式教材

## 目錄

1. [什麼是 Docker Volume？](#什麼是-docker-volume)
2. [Volume 的三種類型](#volume-的三種類型)
3. [基本指令操作](#基本指令操作)
4. [在容器中使用 Volume](#在容器中使用-volume)
5. [docker-compose 中的 Volume](#docker-compose-中的-volume)
6. [常見使用場景](#常見使用場景)
7. [Volume 的進階操作](#volume-的進階操作)
8. [常見問題與注意事項](#常見問題與注意事項)
9. [實戰練習](#實戰練習)

---

## 什麼是 Docker Volume？

Docker 容器的檔案系統預設是**暫時性**的，當容器被刪除後，裡面的資料也會一起消失。為了解決資料持久化的問題，Docker 提供了 **Volume（卷）** 機制。

### 為什麼需要 Volume？

| 問題 | 沒有 Volume | 有 Volume |
|------|-------------|-----------|
| 容器刪除後資料 | 全部消失 | 保留在 Volume 中 |
| 多容器共享資料 | 做不到 | 可以掛載同一個 Volume |
| 備份資料 | 困難 | 可直接備份 Volume 目錄 |
| 效能 | 使用容器層，較慢 | 直接掛載，效能更好 |

### Volume 的核心概念

```
Host 主機                    Container 容器
┌─────────────────┐          ┌─────────────────┐
│                 │          │                 │
│  /var/lib/      │  掛載    │  /app/data      │
│  docker/volumes │ <──────> │                 │
│  /myvolume      │          │                 │
│                 │          │                 │
└─────────────────┘          └─────────────────┘
```

---

## Volume 的三種類型

### 1. Named Volume（具名卷）

由 Docker 管理，儲存在 Docker 的預設目錄（`/var/lib/docker/volumes/`）。

```bash
# 建立 named volume
docker volume create my-data

# 使用 named volume 啟動容器
docker run -v my-data:/app/data nginx
```

**優點：** 易於管理、可跨容器共享、Docker 自動管理路徑。

---

### 2. Bind Mount（綁定掛載）

將 Host 主機上的**指定路徑**直接掛載進容器。

```bash
# 將主機的 /home/user/project 掛載到容器的 /app
docker run -v /home/user/project:/app nginx

# Windows 路徑範例
docker run -v C:\Users\user\project:/app nginx
```

**優點：** 開發時即時同步程式碼、可以直接編輯 Host 上的檔案。

**注意：** 路徑必須使用絕對路徑。

---

### 3. tmpfs Mount（記憶體掛載）

資料儲存在記憶體中，容器停止後即消失。僅 Linux 支援。

```bash
docker run --tmpfs /app/tmp nginx
```

**適用場景：** 儲存暫時性的敏感資料（如 session token），不想寫入磁碟。

---

### 三種類型比較

```
Named Volume          Bind Mount            tmpfs Mount
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Docker 管理  │       │ 使用者指定路 │       │ 記憶體儲存   │
│ 自動建立目錄 │       │ 徑，即時同步 │       │ 容器停止即消 │
│ 易於跨容器   │       │ 適合開發環境 │       │ 失，安全性高 │
│ 共享         │       │             │       │             │
└─────────────┘       └─────────────┘       └─────────────┘
   生產環境推薦            開發環境推薦           敏感資料推薦
```

---

## 基本指令操作

### 建立 Volume

```bash
# 建立一個名為 my-volume 的 Volume
docker volume create my-volume

# 建立時指定 driver（預設為 local）
docker volume create --driver local my-volume
```

### 列出所有 Volume

```bash
docker volume ls

# 輸出範例：
# DRIVER    VOLUME NAME
# local     my-volume
# local     postgres-data
# local     redis-cache
```

### 查看 Volume 詳細資訊

```bash
docker volume inspect my-volume

# 輸出範例：
# [
#   {
#     "CreatedAt": "2026-05-09T10:00:00Z",
#     "Driver": "local",
#     "Labels": {},
#     "Mountpoint": "/var/lib/docker/volumes/my-volume/_data",
#     "Name": "my-volume",
#     "Options": {},
#     "Scope": "local"
#   }
# ]
```

### 刪除 Volume

```bash
# 刪除單一 Volume（Volume 必須未被任何容器使用）
docker volume rm my-volume

# 刪除所有未使用的 Volume（危險！請謹慎使用）
docker volume prune

# 刪除前會提示確認，也可加 -f 強制執行
docker volume prune -f
```

---

## 在容器中使用 Volume

### 使用 `-v` 或 `--volume` 旗標

```bash
# 語法：docker run -v <volume-name 或 host-path>:<container-path> <image>

# Named Volume
docker run -d \
  --name my-container \
  -v my-data:/var/lib/mysql \
  mysql:8.0

# Bind Mount
docker run -d \
  --name web-app \
  -v /home/user/website:/usr/share/nginx/html \
  nginx
```

### 使用 `--mount` 旗標（推薦，語意更清楚）

```bash
# Named Volume
docker run -d \
  --name my-db \
  --mount type=volume,source=db-data,target=/var/lib/mysql \
  mysql:8.0

# Bind Mount
docker run -d \
  --name web-app \
  --mount type=bind,source=/home/user/website,target=/usr/share/nginx/html \
  nginx

# tmpfs Mount
docker run -d \
  --name secure-app \
  --mount type=tmpfs,target=/app/secrets \
  my-app
```

### `-v` 與 `--mount` 的差異

| 項目 | `-v` | `--mount` |
|------|------|-----------|
| 語法 | 簡短 | 較詳細 |
| 可讀性 | 低 | 高 |
| 錯誤提示 | 較不明確 | 較清楚 |
| 自動建立目錄 | 會自動建立 | 不會（Bind Mount 需已存在） |
| 推薦使用 | 快速測試 | 生產環境 |

### 設定唯讀 Volume

```bash
# -v 方式，加上 :ro
docker run -v my-data:/app/config:ro nginx

# --mount 方式
docker run --mount type=volume,source=my-data,target=/app/config,readonly nginx
```

---

## docker-compose 中的 Volume

### 基本範例

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      # Named Volume
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

  web:
    image: nginx
    volumes:
      # Bind Mount（開發時同步程式碼）
      - ./html:/usr/share/nginx/html:ro
    ports:
      - "80:80"

# 宣告 named volumes
volumes:
  postgres-data:
```

### 多容器共享 Volume

```yaml
version: '3.8'

services:
  app:
    image: my-app
    volumes:
      - shared-uploads:/app/uploads

  worker:
    image: my-worker
    volumes:
      # 同一個 volume 掛到不同容器
      - shared-uploads:/worker/uploads

volumes:
  shared-uploads:
```

### 使用外部已存在的 Volume

```yaml
volumes:
  existing-data:
    external: true  # 告訴 Compose 此 Volume 已存在，不要自動建立
```

### Volume 進階設定

```yaml
volumes:
  my-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw
      device: ":/path/to/dir"
    labels:
      com.example.description: "應用資料儲存"
      com.example.environment: "production"
```

---

## 常見使用場景

### 場景一：資料庫持久化

```bash
# MySQL 資料持久化
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=myapp \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# PostgreSQL 資料持久化
docker run -d \
  --name postgres-db \
  -e POSTGRES_PASSWORD=secret \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15
```

### 場景二：開發環境程式碼同步

```bash
# 將本機程式碼掛載進容器，修改即時生效
docker run -d \
  --name dev-server \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:20 \
  npm run dev
```

### 場景三：設定檔管理

```bash
# 將 nginx 設定檔掛載進容器
docker run -d \
  --name nginx \
  -v /etc/nginx/conf.d:/etc/nginx/conf.d:ro \
  -v /var/log/nginx:/var/log/nginx \
  -p 80:80 \
  nginx
```

### 場景四：日誌收集

```bash
# 應用程式將日誌寫入 volume，外部日誌工具讀取
docker run -d \
  --name app \
  -v app-logs:/var/log/app \
  my-application

# 日誌收集工具掛載同一個 volume
docker run -d \
  --name log-shipper \
  -v app-logs:/logs:ro \
  filebeat
```

---

## Volume 的進階操作

### 備份 Volume 資料

```bash
# 使用臨時容器將 volume 資料打包備份到主機
docker run --rm \
  -v my-data:/source:ro \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/my-data-backup.tar.gz -C /source .
```

### 還原 Volume 資料

```bash
# 建立新 volume 並還原資料
docker volume create my-data-restored

docker run --rm \
  -v my-data-restored:/target \
  -v $(pwd):/backup:ro \
  alpine \
  tar xzf /backup/my-data-backup.tar.gz -C /target
```

### 複製 Volume 資料

```bash
# 從一個 volume 複製到另一個 volume
docker run --rm \
  -v source-volume:/source:ro \
  -v target-volume:/target \
  alpine \
  cp -r /source/. /target/
```

### 查看 Volume 內容

```bash
# 啟動臨時容器瀏覽 volume 內容
docker run --rm -it \
  -v my-data:/data \
  alpine \
  sh -c "ls -la /data"
```

### Volume 容量查看

```bash
# 查看所有 volume 占用空間
docker system df -v

# 輸出範例：
# VOLUME NAME    LINKS    SIZE
# my-data        1        1.2GB
# postgres-data  1        512MB
```

---

## 常見問題與注意事項

### 問題一：Volume 資料權限問題

容器內的 user ID 與主機的 user ID 不同時，可能遇到權限錯誤。

```bash
# 解決方式一：在 Dockerfile 中設定正確的 UID
RUN useradd -u 1000 appuser
USER appuser

# 解決方式二：啟動容器時指定 user
docker run -u 1000:1000 -v my-data:/app/data my-image
```

### 問題二：Bind Mount 在 Windows 的路徑問題

```bash
# Windows PowerShell 中使用 ${PWD}
docker run -v ${PWD}:/app node:20

# 或使用完整路徑（注意斜線方向）
docker run -v C:/Users/user/project:/app node:20
```

### 問題三：volume 資料不一致

多個容器同時寫入同一個 Volume 時，可能造成資料不一致。

- 應用層面加鎖，或使用只有單一 writer 的架構
- 使用資料庫管理並發寫入

### 問題四：刪除容器時保留 Volume

```bash
# 預設：刪除容器不會刪除 named volume
docker rm my-container

# 若要同時刪除容器和其 anonymous volume（無名 volume）
docker rm -v my-container
```

### 重要注意事項

1. **Named Volume vs Anonymous Volume**：使用 `-v /app/data` 不指定名稱會產生 anonymous volume，難以管理，**推薦一律使用 named volume**。
2. **生產環境避免 Bind Mount**：Bind Mount 依賴主機路徑，不利於可攜性，生產環境應使用 Named Volume。
3. **定期備份**：Volume 雖然持久化，但主機磁碟損毀仍會導致資料遺失，務必定期備份。
4. **prune 指令謹慎使用**：`docker volume prune` 會刪除所有未使用的 volume，執行前務必確認。

---

## 實戰練習

### 練習一：建立 PostgreSQL + pgAdmin 環境

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    ports:
      - "8080:80"
    depends_on:
      - postgres

volumes:
  postgres-data:
  pgadmin-data:
```

```bash
# 啟動服務
docker compose up -d

# 驗證 volume 已建立
docker volume ls

# 進入 postgres 容器確認資料庫
docker exec -it <postgres-container-id> psql -U admin -d mydb

# 停止並重新啟動，驗證資料持久化
docker compose down
docker compose up -d
```

### 練習二：備份與還原資料庫 Volume

```bash
# 步驟一：備份 postgres-data volume
docker run --rm \
  -v postgres-data:/source:ro \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz -C /source .

# 步驟二：模擬資料遺失（刪除 volume）
docker compose down
docker volume rm <project>_postgres-data

# 步驟三：建立新 volume 並還原
docker volume create <project>_postgres-data
docker run --rm \
  -v <project>_postgres-data:/target \
  -v $(pwd):/backup:ro \
  alpine \
  tar xzf /backup/postgres-backup-20260509.tar.gz -C /target

# 步驟四：重新啟動並驗證資料已還原
docker compose up -d
```

### 練習三：開發環境 Hot Reload

```bash
# 建立 Node.js 專案目錄
mkdir my-app && cd my-app

# 使用 bind mount 啟動開發服務器
docker run -d \
  --name node-dev \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:20 \
  sh -c "npm install && npm run dev"

# 修改本機檔案後，容器內的服務會自動重新載入
```

---

## 總結

| 類型 | 用途 | 推薦環境 |
|------|------|----------|
| Named Volume | 資料庫、應用資料持久化 | 生產環境 |
| Bind Mount | 開發時程式碼同步、設定檔 | 開發環境 |
| tmpfs Mount | 暫時性敏感資料 | 安全性要求高的場景 |

**核心原則：**

- 需要持久化的資料 → 使用 Named Volume
- 開發時需要即時同步 → 使用 Bind Mount
- 敏感且暫時性資料 → 使用 tmpfs
- 定期備份 Volume → 使用 `tar` + 臨時容器

---

> 參考資料：[Docker 官方文件 - Volumes](https://docs.docker.com/storage/volumes/)
