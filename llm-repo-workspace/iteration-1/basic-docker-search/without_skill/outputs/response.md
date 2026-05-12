# Docker 常用指令

## 映像檔（Image）相關

| 指令 | 說明 |
|------|------|
| `docker pull <image>` | 從 Docker Hub 拉取映像檔 |
| `docker images` | 列出本機所有映像檔 |
| `docker build -t <name>:<tag> .` | 根據 Dockerfile 建立映像檔 |
| `docker rmi <image>` | 刪除映像檔 |
| `docker tag <image> <new-name>:<tag>` | 為映像檔加上新標籤 |
| `docker push <image>` | 推送映像檔到 Registry |

## 容器（Container）相關

| 指令 | 說明 |
|------|------|
| `docker run <image>` | 建立並啟動容器 |
| `docker run -d <image>` | 背景模式啟動容器 |
| `docker run -it <image> bash` | 互動模式進入容器 |
| `docker run -p 8080:80 <image>` | 將主機 8080 port 對應容器 80 port |
| `docker run -v /host:/container <image>` | 掛載 Volume |
| `docker run --name <name> <image>` | 指定容器名稱 |
| `docker ps` | 列出執行中的容器 |
| `docker ps -a` | 列出所有容器（含已停止） |
| `docker start <container>` | 啟動已停止的容器 |
| `docker stop <container>` | 停止執行中的容器 |
| `docker restart <container>` | 重新啟動容器 |
| `docker rm <container>` | 刪除容器 |
| `docker rm -f <container>` | 強制刪除執行中的容器 |
| `docker exec -it <container> bash` | 進入執行中容器的 shell |
| `docker logs <container>` | 查看容器日誌 |
| `docker logs -f <container>` | 即時追蹤容器日誌 |
| `docker inspect <container>` | 查看容器詳細資訊（JSON） |
| `docker cp <src> <container>:<dest>` | 複製檔案到容器內 |
| `docker stats` | 即時監控容器資源使用狀況 |

## Volume 相關

| 指令 | 說明 |
|------|------|
| `docker volume create <name>` | 建立 Volume |
| `docker volume ls` | 列出所有 Volume |
| `docker volume inspect <name>` | 查看 Volume 詳細資訊 |
| `docker volume rm <name>` | 刪除 Volume |
| `docker volume prune` | 清除所有未使用的 Volume |

## 網路（Network）相關

| 指令 | 說明 |
|------|------|
| `docker network create <name>` | 建立自訂網路 |
| `docker network ls` | 列出所有網路 |
| `docker network inspect <name>` | 查看網路詳細資訊 |
| `docker network connect <network> <container>` | 將容器加入網路 |
| `docker network rm <name>` | 刪除網路 |

## Docker Compose 相關

| 指令 | 說明 |
|------|------|
| `docker compose up` | 啟動 compose 服務 |
| `docker compose up -d` | 背景模式啟動 compose 服務 |
| `docker compose down` | 停止並移除 compose 服務 |
| `docker compose down -v` | 停止並移除服務及 Volume |
| `docker compose ps` | 列出 compose 服務狀態 |
| `docker compose logs -f` | 即時追蹤 compose 服務日誌 |
| `docker compose build` | 重新建立 compose 服務的映像檔 |
| `docker compose exec <service> bash` | 進入指定服務的容器 |

## 系統清理

| 指令 | 說明 |
|------|------|
| `docker system prune` | 清除所有未使用的資源（容器、映像檔、網路） |
| `docker system prune -a` | 包含未使用的映像檔一併清除 |
| `docker system df` | 查看 Docker 磁碟使用量 |

## 常用 `docker run` 參數整理

| 參數 | 說明 |
|------|------|
| `-d` | 背景執行（detached mode） |
| `-it` | 互動模式 + 偽終端機 |
| `-p <host>:<container>` | Port 對應 |
| `-v <host>:<container>` | Volume 掛載 |
| `--name` | 指定容器名稱 |
| `--rm` | 容器停止後自動刪除 |
| `-e KEY=VALUE` | 設定環境變數 |
| `--network` | 指定網路 |
| `--restart always` | 容器自動重啟策略 |
