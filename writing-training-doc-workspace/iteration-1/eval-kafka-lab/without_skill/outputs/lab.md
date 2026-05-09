# Apache Kafka Consumer Group 機制 Lab

## 學習目標

完成本 Lab 後，學員將能夠：

- 理解 Apache Kafka 的基本架構與核心概念
- 說明 Consumer Group 的設計目的與運作原理
- 實際操作 Kafka Consumer Group，觀察 Partition 分配行為
- 理解 Consumer Group 如何實現負載均衡與容錯

---

## 前置知識：Kafka 是什麼？

在開始 Lab 之前，我們先建立基本概念。

### Kafka 的角色

Apache Kafka 是一套**分散式訊息串流平台**，專門用來處理大量、即時的資料流。你可以把它想像成一個**超高速的公告欄**：

- **Producer（生產者）**：在公告欄貼上訊息的人
- **Consumer（消費者）**：去公告欄讀取訊息的人
- **Topic（主題）**：公告欄上的不同欄位（例如「業績通知」、「系統警報」）
- **Broker（仲介節點）**：公告欄本身，負責儲存與傳遞訊息

### Partition（分區）是什麼？

每個 Topic 可以分成多個 **Partition**。這就像一個主題下有多條收件匣，每條收件匣獨立儲存訊息，可以並行處理。

```
Topic: orders
  ├── Partition 0: [msg-1, msg-4, msg-7, ...]
  ├── Partition 1: [msg-2, msg-5, msg-8, ...]
  └── Partition 2: [msg-3, msg-6, msg-9, ...]
```

Partition 的存在讓 Kafka 能夠**水平擴展**，同時處理更多訊息。

---

## 核心概念：Consumer Group

### 為什麼需要 Consumer Group？

假設你有一個 Topic 每秒產生 10,000 筆訂單訊息，但單一 Consumer 每秒只能處理 3,000 筆。怎麼辦？

答案是：**多個 Consumer 組成一個 Consumer Group，一起分工合作處理訊息。**

### Consumer Group 的運作原理

Consumer Group 是一群擁有**相同 Group ID**的 Consumer 集合。Kafka 會將 Topic 的 Partition 自動分配給 Group 內的成員：

```
Topic: orders (3 個 Partition)

Consumer Group: order-processors
  ├── Consumer A → 負責 Partition 0
  ├── Consumer B → 負責 Partition 1
  └── Consumer C → 負責 Partition 2
```

**關鍵規則：**

1. 同一個 Partition 在同一個 Consumer Group 內，**只會被一個 Consumer 處理**（避免重複消費）
2. 不同的 Consumer Group 可以**各自獨立消費**同一個 Topic（互不干擾）
3. Partition 數量決定了 Consumer Group 內最大有效 Consumer 數量

### Partition 與 Consumer 數量的關係

| Partition 數量 | Consumer 數量 | 結果 |
|:-:|:-:|:--|
| 3 | 1 | 1 個 Consumer 處理全部 3 個 Partition |
| 3 | 3 | 每個 Consumer 各負責 1 個 Partition（最佳狀態） |
| 3 | 5 | 3 個 Consumer 各負責 1 個 Partition，2 個 Consumer 閒置 |

> Consumer 數量超過 Partition 數量時，多出來的 Consumer 不會收到任何訊息。

### Rebalance（重新平衡）

當 Group 內有 Consumer **加入或離開**時，Kafka 會自動觸發 **Rebalance**，重新分配 Partition：

```
初始狀態：
  Consumer A → Partition 0, 1
  Consumer B → Partition 2, 3

Consumer C 加入後（Rebalance）：
  Consumer A → Partition 0
  Consumer B → Partition 1, 2
  Consumer C → Partition 3
```

---

## 環境準備

### 系統需求

- Docker Desktop（已安裝）
- Java 11+（或使用 Docker 內的環境）
- Terminal / Command Prompt

### 啟動 Kafka 環境

建立 `docker-compose.yml` 檔案：

```yaml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

啟動服務：

```bash
docker-compose up -d
```

確認 Kafka 已啟動：

```bash
docker-compose ps
```

---

## Lab 操作步驟

### Step 1：建立 Topic（含多個 Partition）

進入 Kafka container：

```bash
docker exec -it <kafka-container-name> bash
```

建立名為 `lab-orders` 的 Topic，設定 3 個 Partition：

```bash
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --partitions 3 \
  --replication-factor 1
```

確認 Topic 建立成功：

```bash
kafka-topics.sh --describe \
  --bootstrap-server localhost:9092 \
  --topic lab-orders
```

預期輸出：

```
Topic: lab-orders   PartitionCount: 3   ReplicationFactor: 1
  Partition: 0   Leader: 1   Replicas: 1   Isr: 1
  Partition: 1   Leader: 1   Replicas: 1   Isr: 1
  Partition: 2   Leader: 1   Replicas: 1   Isr: 1
```

---

### Step 2：觀察單一 Consumer 的情況

開啟**終端機視窗 A**，啟動第一個 Consumer（屬於 `order-group`）：

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --group order-group \
  --from-beginning
```

開啟**終端機視窗 B**，傳送訊息：

```bash
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders
```

輸入以下測試訊息（每行按 Enter）：

```
order-001
order-002
order-003
order-004
order-005
```

**觀察：** 視窗 A 應該收到所有 5 筆訊息，因為目前只有一個 Consumer，它會處理所有 Partition。

---

### Step 3：加入第二個 Consumer，觀察 Partition 分配

保持視窗 A 的 Consumer 繼續運行。

開啟**終端機視窗 C**，啟動第二個 Consumer（同樣屬於 `order-group`）：

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --group order-group
```

開啟**終端機視窗 D**，繼續發送訊息：

```bash
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders
```

輸入更多訊息：

```
order-006
order-007
order-008
order-009
order-010
```

**觀察：** 視窗 A 和視窗 C 應該**各自收到部分訊息**，這就是 Consumer Group 在分工合作。

> 注意：Kafka 根據訊息的 Key 決定寫入哪個 Partition。沒有指定 Key 時採 Round-Robin 分配，所以每個 Consumer 收到的訊息數量可能不完全相同。

---

### Step 4：加入第三個 Consumer，達到最佳分配狀態

開啟**終端機視窗 E**，啟動第三個 Consumer：

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --group order-group
```

此時 Consumer Group 有 3 個 Consumer、Topic 有 3 個 Partition，**每個 Consumer 各負責一個 Partition**，達到最佳平衡狀態。

查詢 Consumer Group 的分配狀況：

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-group
```

預期輸出類似：

```
GROUP        TOPIC      PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID
order-group  lab-orders  0          4               4               0    consumer-A-xxx
order-group  lab-orders  1          3               3               0    consumer-B-xxx
order-group  lab-orders  2          3               3               0    consumer-C-xxx
```

---

### Step 5：模擬 Consumer 離線，觀察 Rebalance

關閉**視窗 C** 的 Consumer（Ctrl+C）。

等待約 10 秒後，再次查詢分配狀況：

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-group
```

**觀察：** 原本由視窗 C 負責的 Partition，現在應該被重新分配給視窗 A 或視窗 E 的 Consumer。這就是 **Rebalance** 機制自動保障服務可用性。

---

### Step 6：加入第四個 Consumer，觀察閒置情況

開啟**終端機視窗 F**，啟動第四個 Consumer：

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --group order-group
```

查詢分配狀況：

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-group
```

**觀察：** Topic 只有 3 個 Partition，但現在有 3 個 Consumer 正在運行（視窗 A、E、F）。其中一個 Consumer 的 PARTITION 欄位為 `-`，表示它沒有被分配到任何 Partition，處於**閒置等待狀態**。

---

### Step 7：不同 Consumer Group 獨立消費

開啟**終端機視窗 G**，用**不同的 Group ID** 啟動一個新 Consumer：

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic lab-orders \
  --group analytics-group \
  --from-beginning
```

**觀察：** 視窗 G 會從頭讀取 `lab-orders` Topic 的所有歷史訊息。這是因為 `analytics-group` 是全新的 Group，有自己獨立的 Offset 記錄，不受 `order-group` 影響。

---

## 驗收問題

完成以上操作後，請思考並回答以下問題：

**問題 1：** 如果 `lab-orders` Topic 只有 2 個 Partition，但 `order-group` 有 5 個 Consumer，最多幾個 Consumer 能同時收到訊息？為什麼？

**問題 2：** 如果一個 Consumer 在處理訊息時突然當機，Kafka 如何保證這批訊息不會遺失？

**問題 3：** 假設你的系統需要同時支援「訂單處理服務」和「訂單統計分析服務」都讀取同一個 Topic，應該如何設計 Consumer Group？

**問題 4：** 在 Step 4 的 `kafka-consumer-groups.sh` 輸出中，`LAG` 欄位代表什麼意義？LAG 值過大時，代表系統出現了什麼問題？

---

## 重點整理

| 概念 | 說明 |
|:--|:--|
| **Consumer Group** | 多個 Consumer 組成的群組，共同消費一個 Topic |
| **Group ID** | 識別 Consumer Group 的唯一名稱 |
| **Partition 分配** | 每個 Partition 只分配給 Group 內的一個 Consumer |
| **Rebalance** | Consumer 加入/離線時，自動重新分配 Partition |
| **LAG** | Consumer 尚未讀取的訊息數量（越小越好） |
| **獨立消費** | 不同 Group 各自維護 Offset，互不影響 |

### 最佳實踐建議

1. **Partition 數量 >= Consumer 數量**：避免有 Consumer 永遠閒置
2. **合理規劃 Consumer Group**：依業務功能區分，避免不同服務共用同一個 Group
3. **監控 LAG 指標**：LAG 持續增長代表消費速度跟不上生產速度，需要擴充 Consumer
4. **避免頻繁 Rebalance**：過多的加入/離開事件會影響系統穩定性

---

## 清理環境

完成 Lab 後，清理測試資源：

```bash
# 刪除 Topic
kafka-topics.sh --delete \
  --bootstrap-server localhost:9092 \
  --topic lab-orders
```

關閉 Docker 環境：

```bash
docker-compose down
```

---

## 延伸閱讀

- [Apache Kafka 官方文件](https://kafka.apache.org/documentation/)
- [Consumer Group 詳細設計說明](https://kafka.apache.org/documentation/#intro_consumers)
- Kafka Streams：基於 Consumer Group 的串流處理框架
- Confluent Schema Registry：搭配 Kafka 管理訊息格式
