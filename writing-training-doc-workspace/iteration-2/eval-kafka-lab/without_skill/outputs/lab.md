# Apache Kafka Consumer Group 機制 Lab 文件

## 學習目標

完成本 Lab 後，學員將能夠：

- 理解 Apache Kafka 的基本架構與核心概念
- 了解 Consumer Group 是什麼，以及它解決了什麼問題
- 實際建立多個 Consumer，觀察 Partition 如何被分配
- 理解 Rebalance 發生的時機與影響

---

## 前置知識：Kafka 是什麼？

Apache Kafka 是一個**分散式的訊息串流平台**，常用於以下場景：

- 系統之間的非同步溝通
- 即時資料處理 Pipeline
- 事件日誌收集

你可以把 Kafka 想像成一個**快遞中心的物流系統**：

- **Producer**（生產者）：負責寄包裹的人，把訊息送進 Kafka
- **Topic**（主題）：類似快遞分類區，訊息依照類別放在不同的 Topic
- **Partition**（分區）：一個 Topic 可以切成多條平行的輸送帶（Partition）
- **Consumer**（消費者）：負責從輸送帶取包裹的人
- **Consumer Group**：一群協作取包裹的工人，一起消費同一個 Topic

---

## 核心概念：Consumer Group

### 為什麼需要 Consumer Group？

假設一個 Topic 每秒收到 10,000 則訊息，一個 Consumer 每秒只能處理 2,000 則，這時候就需要**多個 Consumer 同時工作**來分擔負載。

Consumer Group 讓多個 Consumer 共同消費一個 Topic，**每個 Partition 在同一時間只會被 Group 內的一個 Consumer 負責**。

### Partition 分配規則

| Consumer 數量 | Partition 數量 | 分配結果 |
|:---:|:---:|:---|
| 1 | 3 | 1 個 Consumer 負責全部 3 個 Partition |
| 2 | 3 | Consumer A 負責 Partition 0, 1；Consumer B 負責 Partition 2 |
| 3 | 3 | 每個 Consumer 各負責 1 個 Partition |
| 4 | 3 | 3 個 Consumer 各負責 1 個，第 4 個**閒置** |

> 重點：Consumer 數量超過 Partition 數量時，多出來的 Consumer 不會收到任何訊息。

### Consumer Group ID

每個 Consumer Group 有一個唯一的 `group.id`。

- 相同 `group.id` 的 Consumer 屬於同一個 Group，**彼此競爭** Partition
- 不同 `group.id` 的 Consumer 屬於不同 Group，**各自獨立**消費全部 Partition

這表示你可以讓多個不同的應用程式**各自完整地讀取**同一份資料流。

---

## 環境準備

### 系統需求

- Docker Desktop（已安裝並啟動）
- Terminal（PowerShell、Bash 均可）

### 啟動 Kafka 環境

建立一個 `docker-compose.yml` 檔案，內容如下：

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

啟動環境：

```bash
docker compose up -d
```

確認服務正常運行：

```bash
docker compose ps
```

預期看到 `zookeeper` 與 `kafka` 的狀態都是 `Up`。

---

## Lab 1：建立 Topic 並觀察 Partition

### 步驟 1：建立一個有 3 個 Partition 的 Topic

```bash
docker exec -it <kafka-container-name> \
  kafka-topics --create \
  --topic lab-topic \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
```

> 將 `<kafka-container-name>` 替換為你的 Kafka container 名稱（可用 `docker ps` 查詢）

### 步驟 2：確認 Topic 建立成功

```bash
docker exec -it <kafka-container-name> \
  kafka-topics --describe \
  --topic lab-topic \
  --bootstrap-server localhost:9092
```

預期輸出：

```
Topic: lab-topic  PartitionCount: 3  ReplicationFactor: 1
  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
  Partition: 1  Leader: 1  Replicas: 1  Isr: 1
  Partition: 2  Leader: 1  Replicas: 1  Isr: 1
```

**觀察重點：** 這個 Topic 有 3 個 Partition（0、1、2），分別獨立儲存訊息。

---

## Lab 2：單一 Consumer 消費所有 Partition

### 步驟 1：開啟 Consumer（Terminal 1）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

### 步驟 2：另開 Terminal，送出訊息（Terminal 2）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-producer \
  --topic lab-topic \
  --bootstrap-server localhost:9092
```

輸入以下訊息並按 Enter 送出：

```
Hello Kafka
This is message 2
This is message 3
```

### 步驟 3：觀察 Consumer 視窗

Terminal 1 的 Consumer 應該收到這些訊息。

**觀察重點：** 目前只有 1 個 Consumer，它獨自負責全部 3 個 Partition。

### 步驟 4：查看 Group 的 Partition 分配狀況

開啟第三個 Terminal，執行：

```bash
docker exec -it <kafka-container-name> \
  kafka-consumer-groups \
  --describe \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

你會看到類似這樣的輸出：

```
GROUP           TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID
my-first-group  lab-topic  0         1               1               0    consumer-1-...
my-first-group  lab-topic  1         1               1               0    consumer-1-...
my-first-group  lab-topic  2         1               1               0    consumer-1-...
```

**觀察重點：** 全部 3 個 Partition 都由同一個 `CONSUMER-ID` 負責。

---

## Lab 3：加入第二個 Consumer，觀察 Rebalance

### 步驟 1：保持 Lab 2 的 Consumer 繼續運行

Terminal 1 的 Consumer 持續運行。

### 步驟 2：加入第二個 Consumer（Terminal 3）

使用**相同的 group.id**：

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

### 步驟 3：觀察兩個 Consumer 的輸出

你可能會注意到 Terminal 1 短暫停止接收訊息——這就是 **Rebalance** 正在發生。

Rebalance 完成後，兩個 Consumer 會各自負責部分 Partition。

### 步驟 4：再次查看 Partition 分配

```bash
docker exec -it <kafka-container-name> \
  kafka-consumer-groups \
  --describe \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

預期輸出（分配可能因 Kafka 版本略有不同）：

```
GROUP           TOPIC     PARTITION  CONSUMER-ID
my-first-group  lab-topic  0         consumer-1-...
my-first-group  lab-topic  1         consumer-1-...
my-first-group  lab-topic  2         consumer-2-...
```

**觀察重點：** 現在兩個不同的 `CONSUMER-ID` 分別負責不同的 Partition。

### 步驟 5：送出更多訊息，觀察分配行為

在 Terminal 2（Producer）繼續輸入：

```
message-A
message-B
message-C
message-D
message-E
```

觀察訊息是否分別出現在不同的 Consumer 視窗中。

> 注意：同一個 Partition 的訊息只會被同一個 Consumer 收到，所以訊息**不會**平均分散到兩個視窗，而是依照 Partition 路由分配。

---

## Lab 4：Consumer 數量超過 Partition 數量

### 步驟 1：加入第三個 Consumer（Terminal 4）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

現在有 3 個 Consumer，剛好對應 3 個 Partition，每人負責 1 個。

### 步驟 2：加入第四個 Consumer（Terminal 5）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

### 步驟 3：查看 Partition 分配

```bash
docker exec -it <kafka-container-name> \
  kafka-consumer-groups \
  --describe \
  --group my-first-group \
  --bootstrap-server localhost:9092
```

你會看到其中一個 Consumer 的 `PARTITION` 欄位顯示為空，代表它**沒有負責任何 Partition**，不會收到任何訊息。

**觀察重點：** Consumer 數量超過 Partition 數量時，多出來的 Consumer 是閒置的備援節點。

---

## Lab 5：不同 Group 各自獨立消費

### 步驟 1：關閉所有現有的 Consumer

按 `Ctrl+C` 結束 Lab 3、4 中所有的 Consumer。

### 步驟 2：啟動 Group A 的 Consumer（Terminal 1）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group group-A \
  --from-beginning \
  --bootstrap-server localhost:9092
```

### 步驟 3：啟動 Group B 的 Consumer（Terminal 2）

```bash
docker exec -it <kafka-container-name> \
  kafka-console-consumer \
  --topic lab-topic \
  --group group-B \
  --from-beginning \
  --bootstrap-server localhost:9092
```

### 步驟 4：觀察兩個視窗

兩個視窗都應該看到**所有**歷史訊息，因為它們屬於不同的 Consumer Group，彼此完全獨立，各自從頭讀取。

**觀察重點：** 不同的 Group 代表不同的消費進度，互不干擾。這讓不同的應用程式（例如一個做資料分析、一個做即時通知）可以各自完整消費同一個 Topic。

---

## 概念總結

```
Topic: lab-topic（3 個 Partition）
├── Partition 0
├── Partition 1
└── Partition 2

Consumer Group: my-first-group
├── Consumer A → Partition 0
├── Consumer B → Partition 1
└── Consumer C → Partition 2

Consumer Group: group-B（獨立的 Group，各自消費全部 Partition）
├── Consumer X → Partition 0, 1, 2
```

| 概念 | 說明 |
|:---|:---|
| Consumer Group | 一組共同消費 Topic 的 Consumer，彼此分工 |
| Partition 分配 | 同一 Group 內，每個 Partition 只給一個 Consumer |
| Rebalance | Consumer 加入或離開時，Partition 重新分配的過程 |
| 獨立消費 | 不同 Group 各自維護消費進度，互不影響 |
| 閒置 Consumer | Consumer 數量超過 Partition 時，多出來的 Consumer 不收訊息 |

---

## 清理環境

實驗完成後，關閉並移除 Docker 服務：

```bash
docker compose down
```

---

## 延伸思考

1. 如果一個 Consumer 在處理訊息時崩潰，Kafka 會怎麼處理那些 Partition？
2. 為什麼 Partition 數量的設定在建立 Topic 時需要謹慎考量？
3. 在生產環境中，Consumer Group 的 `group.id` 應該如何命名與管理？
4. `--from-beginning` 參數代表什麼？如果不加，Consumer 會從哪裡開始讀？
