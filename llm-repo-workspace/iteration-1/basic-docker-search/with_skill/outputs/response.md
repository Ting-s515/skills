# Docker 常用指令

根據 `[[docker]]` wiki 頁面，以下是 Docker 的常用指令整理：

---

## 建置與運行

| 指令 | 說明 |
|------|------|
| `docker build -t <名稱> .` | 建置映像檔 |
| `docker build --no-cache -t <名稱> .` | 不使用快取建置 |
| `docker run -d -p <主機埠>:<容器埠> --name <名稱> <映像檔>` | 背景運行容器 |
| `docker run -it <映像檔> /bin/sh` | 互動模式進入 shell |

---

## 容器管理

| 指令 | 說明 |
|------|------|
| `docker ps` | 列出運行中容器 |
| `docker ps -a` | 列出所有容器（含停止） |
| `docker stop/start/restart <容器>` | 停止 / 啟動 / 重啟容器 |
| `docker rm <容器>` | 刪除容器 |
| `docker rm -f <容器>` | 強制刪除容器 |

---

## 監控與除錯

| 指令 | 說明 |
|------|------|
| `docker logs -f <容器>` | 即時跟蹤 log |
| `docker exec -it <容器> /bin/sh` | 進入容器 shell |
| `docker inspect <容器>` | 查看容器詳細資訊 |
| `docker stats` | 顯示資源使用情況 |

---

## 系統清理

| 指令 | 說明 |
|------|------|
| `docker system prune` | 清理未使用資源 |
| `docker system prune -a` | 清理所有未使用資源（含映像檔） |

---

## 重新建置流程（一行指令）

```bash
docker stop my-app && docker rm my-app && docker build -t my-app . && docker run -d -p 3000:3000 --name my-app my-app
```

此流程依序執行：停止 → 刪除 → 重新建置 → 啟動，適合開發過程中快速重部署。

---

## 資料來源

- wiki 頁面：`[[docker]]`（`pages/docker.md`）
- 相關延伸：`[[docker-compose]]` — 多容器服務編排工具
