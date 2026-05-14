# 任務清單：報表匯出

## 參考文檔
- 結構化流程：`backend/docs/propose/report-export/01-flow.md`
- 驗收條件：`backend/docs/propose/report-export/02-gherkin.md`

## 任務

- [ ] T1: 建立 ReportExportController，定義 POST /api/reports/export 端點（影響：`src/controllers/report-export.controller.ts`）
- [ ] T2: 建立輸入驗證 DTO（日期格式、start <= end、區間 <= 365 天、format 合法值）（影響：`src/dto/report-export.dto.ts`）（依賴 T1）
- [ ] T3: 實作 ReportExportService，查詢已完成訂單並依日期區間與類別篩選（影響：`src/services/report-export.service.ts`）（依賴 T1）
- [ ] T4: 實作 Excel 格式產生（.xlsx），空資料時回傳僅含標題列（影響：`src/services/report-export.service.ts`）（依賴 T3）
- [ ] T5: 實作 CSV 格式產生（UTF-8 with BOM），空資料時回傳僅含標題列（影響：`src/services/report-export.service.ts`）（依賴 T3）
- [ ] T6: 設定 HTTP 附件回應 header，依 format 設定對應 MIME type（影響：`src/controllers/report-export.controller.ts`）（依賴 T4, T5）
- [ ] T7: 加入路由層的權限守衛（未登入 401，無匯出權限 403）（依賴 T1）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
