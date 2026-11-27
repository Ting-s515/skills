# 好測試與壞測試

## 好測試

整合風格：透過真實介面測試，而不是替換內部零件。

```ts
// 好：透過 API 驗證可觀察的行為（後端整合測試，以 supertest 為例）
it('Given重複的ID_When批次刪除_Should每筆只刪一次', async () => {
  const first = await createItem({ name: 'a' })
  const second = await createItem({ name: 'b' })

  const res = await request(app)
    .post('/items/batch-delete')
    .send({ ids: [first.id, second.id, first.id] })

  expect(res.status).toBe(200)
  expect(res.body.deletedIds).toEqual([first.id, second.id])
})
```

```ts
// 好：透過公開函式驗證行為（前端單元測試）
it('Given前次載入失敗_When再次取得_Should允許重新請求', async () => {
  const load = vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValue(currentUser)
  const loader = createCurrentUserLoader(load)

  await expect(loader()).rejects.toThrow('offline')
  await expect(loader()).resolves.toEqual(currentUser)
})
```

特徵：

- 測的是使用者／呼叫端在意的行為
- 只用公開 API
- 內部重構後依然成立
- 描述「做什麼」，而不是「怎麼做」
- 每個測試只有一個邏輯上的斷言

## 壞測試

實作細節測試：與內部結構耦合。

```java
// 壞：測的是實作細節
@Test
void delete_disabledItem_callsRepositoryAndTeardown() {
    service.delete(id);

    verify(repository).deleteById(id);
    verify(teardownTasks).save(any());
}
```

警訊：

- 替換內部協作者
- 測試私有方法
- 斷言呼叫次數／呼叫順序
- 沒有改變行為的重構讓測試壞掉
- 測試名稱描述「怎麼做」而不是「做什麼」
- 透過外部手段驗證，而不是透過介面

```ts
// 壞：繞過介面，直接查資料表驗證
it('建立項目', async () => {
  await request(app).post('/items').send({ name: 'timeout', value: '30' })

  const rows = await db.query("select * from item where name = 'timeout'")
  expect(rows).toHaveLength(1)
})

// 好：透過介面驗證
it('建立的項目可以查到明細', async () => {
  const created = await request(app).post('/items').send({ name: 'timeout', value: '30' })

  const detail = await request(app).get(`/items/${created.body.id}`)
  expect(detail.body).toMatchObject({ name: 'timeout', value: '30' })
})
```

若專案的測試框架提供「驗證資料表結果」的標準指令，且資料庫是測試專用的隔離環境（如 Testcontainers），依專案慣例使用不算繞過介面。仍然要避免的：

- 自寫測試程式直接下 SQL 查表或改表。
- 直接讀寫其他模組的資料；其他模組的資料一律經該模組的 API 建立與讀取。
- 測試連到共用或真實環境的資料庫。

套套邏輯測試：預期值只是把實作重述一次，所以測試天生會通過。

```java
// 壞：用程式碼的同一套算法重算預期值
@Test
void totalBytes_twoFiles_sumsSizes() {
    var files = List.of(new FileEntry("a.csv", 10), new FileEntry("b.csv", 5));
    long expected = files.stream().mapToLong(FileEntry::size).sum();
    assertThat(FileSummary.totalBytes(files)).isEqualTo(expected);
}

// 好：預期值是獨立、已知的字面值
@Test
void totalBytes_twoFiles_sumsSizes() {
    var files = List.of(new FileEntry("a.csv", 10), new FileEntry("b.csv", 5));
    assertThat(FileSummary.totalBytes(files)).isEqualTo(15);
}
```
