import { readFile } from "node:fs/promises";
import path from "node:path";

const inputPath = path.resolve(process.argv[2] ?? process.cwd());
const webDirectory =
  path.basename(inputPath).toLowerCase() === "docs-web"
    ? inputPath
    : path.join(inputPath, "docs-web");
const failures = [];

async function read(relativePath) {
  try {
    return await readFile(path.join(webDirectory, relativePath), "utf8");
  } catch (error) {
    failures.push(`${relativePath}: 無法讀取 (${error.code ?? error.message})`);
    return "";
  }
}

function requireMatch(content, pattern, message) {
  if (!pattern.test(content)) {
    failures.push(message);
  }
}

function rejectMatch(content, pattern, message) {
  if (pattern.test(content)) {
    failures.push(message);
  }
}

const [
  packageSource,
  buildSource,
  serverSource,
  html,
  app,
  codeCopySource,
  dialogKeydownSource,
  style,
  testSource,
] = await Promise.all([
    read("package.json"),
    read("script/build-site.mjs"),
    read("script/server.mjs"),
    read("src/index.html"),
    read("src/app.mjs"),
    read("src/code-copy.mjs"),
    read("src/dialog-keydown.mjs"),
    read("src/style.css"),
    read("test/build-site.test.mjs"),
  ]);

if (packageSource) {
  try {
    const packageJson = JSON.parse(packageSource);
    const expectedScripts = {
      build: "node ./script/build-site.mjs",
      dev: "npm run build && node ./script/server.mjs",
      preview: "node ./script/server.mjs",
      test: "node --test ./test/*.test.mjs",
    };

    if (packageJson.type !== "module") {
      failures.push('package.json: type 必須為 "module"');
    }

    for (const [name, command] of Object.entries(expectedScripts)) {
      if (packageJson.scripts?.[name] !== command) {
        failures.push(`package.json: scripts.${name} 必須為 ${command}`);
      }
    }
  } catch (error) {
    failures.push(`package.json: JSON 格式錯誤 (${error.message})`);
  }
}

requireMatch(buildSource, /remarkGfm/, "build-site.mjs: 缺少 GFM render");
requireMatch(
  buildSource,
  /className:\s*\["mermaid"\]/,
  "build-site.mjs: Mermaid code fence 未轉為 .mermaid",
);
requireMatch(
  buildSource,
  /DOCUMENT_NAVIGATION[\s\S]*DOCUMENT_CONTENT/,
  "build-site.mjs: 缺少單頁導覽或內容注入",
);
requireMatch(serverSource, /const port = 18100;/, "server.mjs: port 必須為 18100");
requireMatch(serverSource, /const host = "127\.0\.0\.1";/, "server.mjs: host 必須為 127.0.0.1");
requireMatch(html, /id="diagram-dialog"/, "index.html: 缺少 Mermaid dialog");
requireMatch(html, /data-diagram-action="zoom-in"/, "index.html: 缺少 Mermaid zoom controls");
requireMatch(app, /securityLevel:\s*"strict"/, "app.mjs: Mermaid 必須使用 strict security level");
requireMatch(app, /dialog\.showModal\(\)/, "app.mjs: 缺少 dialog 開啟行為");
requireMatch(
  app,
  /button\.className = "code-copy-button"/,
  "app.mjs: 缺少 code block 複製按鈕",
);
requireMatch(
  app,
  /copyCodeToClipboard\(code\.textContent \?\? "", navigator\.clipboard\)/,
  "app.mjs: 複製內容必須取自 code textContent",
);
requireMatch(app, /createSvgElement\("rect"/, "app.mjs: 缺少 Copy SVG icon");
requireMatch(app, /createSvgElement\("path"/, "app.mjs: 缺少 Check SVG icon");
requireMatch(
  app,
  /setCodeCopyButtonState\(button, "success"\)/,
  "app.mjs: 缺少複製成功 icon 狀態",
);
requireMatch(
  app,
  /setCodeCopyButtonState\(button, "error"\)/,
  "app.mjs: 缺少複製失敗 icon 狀態",
);
requireMatch(
  app,
  /button\.dataset\.tooltip = presentation\.tooltip/,
  "app.mjs: 缺少複製按鈕 tooltip 狀態",
);
requireMatch(
  app,
  /button\.setAttribute\("aria-label", presentation\.label\)/,
  "app.mjs: 缺少複製按鈕動態 aria-label",
);
rejectMatch(
  app,
  /button\.textContent = "(?:複製|已複製|複製失敗)"/,
  "app.mjs: 複製按鈕不得顯示可見文字",
);
requireMatch(
  codeCopySource,
  /export async function copyCodeToClipboard/,
  "code-copy.mjs: 缺少可測試的 Clipboard helper",
);
requireMatch(codeCopySource, /clipboard\.writeText\(text\)/, "code-copy.mjs: 缺少文字寫入行為");
requireMatch(
  app,
  /dialog\.addEventListener\("keydown",[\s\S]*closeDialogOnEscape/,
  "app.mjs: 未接上明確的 Esc 關閉 helper",
);
requireMatch(
  dialogKeydownSource,
  /export function closeDialogOnEscape/,
  "dialog-keydown.mjs: 缺少可測試的 Esc 關閉 helper",
);
requireMatch(app, /addEventListener\(\s*"wheel"/, "app.mjs: 缺少滾輪縮放");
requireMatch(app, /addEventListener\("pointermove"/, "app.mjs: 缺少拖曳行為");
rejectMatch(app, /\bfetch\s*\(/, "app.mjs: 禁止 runtime fetch Markdown");

for (const token of [
  "--page-background: #faf7ef",
  "--sidebar-background: #f4eddf",
  "--content-background: #fffdf8",
  "--code-background: #403b33",
]) {
  if (!style.includes(token)) {
    failures.push(`style.css: 缺少固定 token ${token}`);
  }
}

requireMatch(
  style,
  /\.document-shell\s*{[^}]*grid-template-columns:\s*minmax\(270px, 320px\)\s*minmax\(0, 1fr\)/s,
  "style.css: 缺少固定兩欄 layout",
);
requireMatch(
  style,
  /\.markdown-body\s*{[^}]*max-width:\s*980px/s,
  "style.css: Markdown 卡片最大寬度必須為 980px",
);
requireMatch(
  style,
  /\.mermaid-frame\s*{[^}]*width:\s*100%/s,
  "style.css: Mermaid 必須限制於正文寬度",
);
rejectMatch(
  style,
  /calc\(100vw\s*-\s*320px/,
  "style.css: Mermaid 不得使用 viewport 計算突破正文",
);
requireMatch(style, /\.diagram-dialog::backdrop/, "style.css: 缺少 dialog backdrop");
requireMatch(
  style,
  /\.code-block-frame\s*{[^}]*display:\s*grid/s,
  "style.css: code block frame 必須使用 Grid",
);
requireMatch(
  style,
  /\.code-block-frame\s*{[^}]*grid-template-columns:\s*minmax\(0, 1fr\) 3rem/s,
  "style.css: code block 必須使用指令欄與 3rem 控制欄",
);
requireMatch(
  style,
  /\.code-block-frame pre\s*{[^}]*grid-column:\s*1/s,
  "style.css: 指令必須位於 Grid 左欄",
);
requireMatch(
  style,
  /\.code-block-frame pre\s*{[^}]*min-width:\s*0/s,
  "style.css: 指令欄必須允許縮小並獨立捲動",
);
rejectMatch(
  style,
  /\.code-block-frame pre\s*{[^}]*padding-right:\s*3\.5rem/s,
  "style.css: 指令欄不得以右側 padding 模擬控制欄",
);
rejectMatch(
  style,
  /\.code-block-frame pre\s*{[^}]*padding-top:\s*3\.25rem/s,
  "style.css: code block 不得為複製按鈕增加上方預留列",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*position:\s*relative/s,
  "style.css: 複製按鈕必須以 Grid item 定位 tooltip",
);
rejectMatch(
  style,
  /\.code-copy-button\s*{[^}]*position:\s*absolute/s,
  "style.css: 複製按鈕不得覆蓋指令欄",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*grid-column:\s*2/s,
  "style.css: 複製按鈕必須位於 Grid 右欄",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*align-self:\s*start/s,
  "style.css: 複製按鈕必須位於控制欄頂端",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*justify-self:\s*center/s,
  "style.css: 複製按鈕必須在控制欄水平置中",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*width:\s*2rem/s,
  "style.css: icon-only 複製按鈕寬度必須為 2rem",
);
requireMatch(
  style,
  /\.code-copy-button\s*{[^}]*height:\s*2rem/s,
  "style.css: icon-only 複製按鈕高度必須為 2rem",
);
requireMatch(
  style,
  /\.code-copy-button::before\s*{[^}]*content:\s*attr\(data-tooltip\)/s,
  "style.css: 複製按鈕缺少 CSS tooltip",
);
requireMatch(
  style,
  /\.code-copy-button::before\s*{[^}]*right:\s*calc\(100% \+ 0\.55rem\)/s,
  "style.css: 複製 tooltip 必須從按鈕左側展開",
);
requireMatch(
  style,
  /\.code-copy-button:focus-visible::before/,
  "style.css: 鍵盤 focus 時必須顯示複製 tooltip",
);
requireMatch(
  style,
  /\.code-copy-icon\s*{[^}]*width:\s*0\.875rem/s,
  "style.css: 複製 icon 寬度必須為 0.875rem",
);
requireMatch(
  style,
  /\.code-copy-icon\s*{[^}]*height:\s*0\.875rem/s,
  "style.css: 複製 icon 高度必須為 0.875rem",
);
requireMatch(
  style,
  /@media print[\s\S]*\.code-block-frame\s*{[^}]*grid-template-columns:\s*minmax\(0, 1fr\)/s,
  "style.css: 列印時必須移除複製按鈕控制欄",
);
requireMatch(testSource, /doesNotMatch\(source,\s*\/\\bfetch/, "測試缺少 runtime fetch 防線");
requireMatch(
  testSource,
  /GivenCodeText_WhenCopySucceeds_ShouldPreserveExactContent/,
  "測試缺少完整複製 code text 行為",
);
requireMatch(
  testSource,
  /GivenClipboardUnavailable_WhenCopyCode_ShouldReject/,
  "測試缺少 Clipboard API 不可用分支",
);
requireMatch(
  testSource,
  /doesNotMatch\(source,\s*\/button\\\.textContent/,
  "測試缺少 icon-only 可見文字防線",
);
requireMatch(testSource, /mermaid-frame/, "測試缺少 Mermaid 正文寬度防線");
requireMatch(
  testSource,
  /GivenMermaidDialogOpen_WhenPressEscape_ShouldPreventDefaultAndClose/,
  "測試缺少 Escape 關閉行為防線",
);
requireMatch(
  testSource,
  /GivenMermaidDialogOpen_WhenPressNonEscape_ShouldRemainOpen/,
  "測試缺少非 Escape 鍵的邊界防線",
);

if (failures.length > 0) {
  console.error("靜態教材網站驗證失敗：");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exitCode = 1;
} else {
  console.log(`靜態教材網站驗證通過：${webDirectory}`);
}
