# 任務

替 Linux 平台工程教材網站加入 code block 複製功能。Code block 必須使用雙欄 Grid：指令在可縮小的左欄獨立水平捲動，按鈕位於固定右欄，不能以 absolute positioning 疊在指令上，也不得增加單行 code block 的高度。每個按鈕只顯示內嵌的重疊方框 Copy SVG，不顯示文字或 emoji。Hover 與 keyboard focus 時，tooltip 從按鈕左側展開；複製成功切換為 Check SVG，失敗則保留 Copy SVG 並使用警示色。學員需要快速複製 Bash 與 YAML 範例，但 Mermaid 圖表維持既有放大閱讀器，不應顯示複製按鈕。
