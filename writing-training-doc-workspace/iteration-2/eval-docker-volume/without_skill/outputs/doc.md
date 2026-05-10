# Docker Volume 使用方式教材

## 學習目標

完成本教材後，你將能夠：

- 理解 Docker Volume 的概念與作用
- 區分 Volume、Bind Mount、tmpfs 三種儲存方式
- 建立、掛載、管理 Docker Volume
- 在容器間共享資料
- 應用 Volume 於實際開發情境

---

## 1. 為什麼需要 Docker Volume？

Docker 容器的檔案系統是**暫時性**的。當容器被刪除，所有容器內的資料也會一併消失。

```
容器啟動 → 寫入資料 → 容器刪除 → 資料消失 ❌
```

**Volume 解決了這個問題：**

```
容器啟動 → 掛載 Volume → 寫入資料 → 容器刪除 → 資料仍保留在 Volume ✓
```

**Volume 的主要用途：**

- 資料庫檔案的持久化（MySQL、PostgreSQL）
- 應用程式設定檔的共享
- 開發時的程式碼即時同步
- 多個容器間的資料共享

---

## 2. Docker 儲存方式總覽

| 類型 | 儲存位置 | 適用情境 |
|------|----------|----------|
| **Volume** | Docker 管理的主機目錄（`/var/lib/docker/volumes/`） | 生產環境資料持久化、容器間共享 |
| **Bind Mount** | 主機上任意路徑 | 開發時程式碼同步 |
| **tmpfs Mount** | 主機記憶體 | 敏感性暫存資料，不需持久化 |

---

## 3. Volume 基本操作

### 3.1 建立 Volume

```bash
# 建立一個具名 Volume
docker volume create my-data

# 查看所有 Volume
docker volume ls

# 查看 Volume 詳細資訊
docker volume inspect my-data
```

`docker volume inspect` 的輸出範例：

```json
[
    {
        "CreatedAt": "2024-01-15T10:30:00Z",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/my-data/_data",
        "Name": "my-data",
        "Options": {},
        "Scope": "local"
    }
]
```

### 3.2 掛載 Volume 到容器

**方式一：使用 `-v` 旗標（簡短語法）**

```bash
docker run -d \
  --name my-container \
  -v my-data:/app/data \
  nginx
```

格式：`-v <volume名稱>:<容器內路徑>`

**方式二：使用 `--mount` 旗標（明確語法，推薦）**

```bash
docker run -d \
  --name my-container \
  --mount type=volume,source=my-data,target=/app/data \
  nginx
```

`--mount` 語法更清楚，適合生產環境使用。

### 3.3 刪除 Volume

```bash
# 刪除指定 Volume（Volume 不可被使用中的容器掛載）
docker volume rm my-data

# 刪除所有未使用的 Volume（清理空間）
docker volume prune
```

---

## 4. 匿名 Volume vs 具名 Volume

### 匿名 Volume

不指定 Volume 名稱，Docker 自動產生一個隨機 ID。

```bash
docker run -d -v /app/data nginx
```

缺點：難以追蹤和管理，容器刪除後不容易找回對應的 Volume。

### 具名 Volume（建議使用）

```bash
docker run -d -v my-data:/app/data nginx
```

優點：名稱清楚，方便管理與跨容器共用。

---

## 5. Bind Mount（綁定掛載）

Bind Mount 直接將主機的目錄或檔案掛載到容器中。

```bash
# 將主機當前目錄掛載到容器的 /app
docker run -d \
  --name dev-container \
  -v $(pwd):/app \
  node:18
```

**開發情境應用：**

```bash
# 開發時同步本機程式碼
docker run -it \
  --name my-app-dev \
  -v $(pwd)/src:/app/src \
  -p 3000:3000 \
  my-node-app npm run dev
```

本機修改 `src/` 下的檔案，容器內立即同步，不需重建 Image。

**Bind Mount 注意事項：**

- 容器對主機目錄有完整讀寫權限，使用時需謹慎
- 主機路徑必須事先存在
- 不同作業系統路徑格式不同（Windows 需使用 `/c/Users/...` 格式）

---

## 6. 實際應用範例

### 6.1 MySQL 資料庫持久化

沒有 Volume 時，刪除容器後資料庫資料全部消失。加上 Volume 後資料可以保留：

```bash
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=myapp \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0
```

即使容器被刪除，重新建立容器並掛載同一個 Volume，資料仍然存在：

```bash
# 刪除容器
docker rm -f mysql-db

# 重新建立，資料依然保留
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0
```

### 6.2 多個容器共享 Volume

多個容器可以掛載同一個 Volume 來共享資料：

```bash
# 建立 Volume
docker volume create shared-logs

# 容器一：寫入日誌
docker run -d \
  --name app-server \
  -v shared-logs:/app/logs \
  my-app

# 容器二：讀取日誌（例如日誌收集工具）
docker run -d \
  --name log-collector \
  -v shared-logs:/logs:ro \
  log-collector-image
```

`:ro` 表示唯讀（read-only），避免日誌收集器意外修改資料。

### 6.3 搭配 Docker Compose

在 `docker-compose.yml` 中宣告 Volume 是最常見的做法：

```yaml
version: "3.8"

services:
  web:
    image: my-app:latest
    volumes:
      - app-data:/app/data
      - ./config:/app/config:ro  # Bind Mount，唯讀

  db:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

volumes:
  app-data:
  postgres-data:
```

執行：

```bash
docker compose up -d
```

Docker Compose 會自動建立宣告的 Volume，名稱會加上專案名稱前綴（如 `myproject_postgres-data`）。

---

## 7. Volume 備份與還原

### 備份 Volume

```bash
# 建立暫時容器，將 Volume 內容打包成 tar 檔
docker run --rm \
  -v my-data:/source:ro \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/my-data-backup.tar.gz -C /source .
```

### 還原 Volume

```bash
# 建立新的 Volume
docker volume create my-data-restored

# 將備份解壓到新 Volume
docker run --rm \
  -v my-data-restored:/target \
  -v $(pwd):/backup:ro \
  alpine \
  tar xzf /backup/my-data-backup.tar.gz -C /target
```

---

## 8. 常見問題與最佳實踐

### 常見問題

**Q：Volume 和 Bind Mount 什麼時候用哪個？**

- 生產環境資料持久化 → 使用 **Volume**
- 開發時程式碼同步 → 使用 **Bind Mount**
- 需要跨平台一致性 → 使用 **Volume**

**Q：容器刪除後 Volume 還在嗎？**

是的。`docker rm` 只刪除容器，Volume 不受影響。若要連同 Volume 一起刪除，需使用 `docker rm -v <container>`。

**Q：如何查看容器掛載了哪些 Volume？**

```bash
docker inspect <容器名稱> --format '{{json .Mounts}}'
```

### 最佳實踐

1. **使用具名 Volume**：避免使用匿名 Volume，方便管理
2. **最小權限原則**：唯讀的資料來源加上 `:ro`，避免意外修改
3. **定期備份**：重要資料的 Volume 應設定備份機制
4. **定期清理**：執行 `docker volume prune` 清理未使用的 Volume，釋放磁碟空間
5. **使用 Docker Compose 集中管理**：在 `docker-compose.yml` 統一宣告所有 Volume

---

## 9. 快速指令總覽

```bash
# 建立 Volume
docker volume create <名稱>

# 列出所有 Volume
docker volume ls

# 查看 Volume 詳細資訊
docker volume inspect <名稱>

# 刪除 Volume
docker volume rm <名稱>

# 清理所有未使用的 Volume
docker volume prune

# 掛載 Volume 啟動容器
docker run -v <volume名稱>:<容器路徑> <image>

# 掛載 Bind Mount
docker run -v <主機路徑>:<容器路徑> <image>

# 唯讀掛載
docker run -v <名稱>:<容器路徑>:ro <image>
```

---

## 10. 練習題

**練習一：基本 Volume 操作**

1. 建立一個名為 `practice-vol` 的 Volume
2. 啟動一個 Alpine 容器並掛載該 Volume 到 `/data`
3. 在容器內建立一個檔案：`echo "hello volume" > /data/test.txt`
4. 退出並刪除容器
5. 重新啟動另一個 Alpine 容器掛載同一個 Volume，確認 `test.txt` 仍然存在

**練習二：Docker Compose 與 Volume**

1. 建立一個 `docker-compose.yml`，包含 WordPress 和 MySQL
2. 為 MySQL 資料目錄和 WordPress 上傳目錄各設定一個 Volume
3. 啟動服務，新增一篇文章
4. 執行 `docker compose down` 再 `docker compose up -d`，確認文章仍然存在

---

## 參考資料

- [Docker 官方文件 - Volumes](https://docs.docker.com/storage/volumes/)
- [Docker 官方文件 - Bind Mounts](https://docs.docker.com/storage/bind-mounts/)
- [Docker Compose - Volumes](https://docs.docker.com/compose/compose-file/07-volumes/)
