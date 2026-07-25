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
  dialogKeydownSource,
  style,
  testSource,
] = await Promise.all([
    read("package.json"),
    read("script/build-site.mjs"),
    read("script/server.mjs"),
    read("src/index.html"),
    read("src/app.mjs"),
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
requireMatch(testSource, /doesNotMatch\(source,\s*\/\\bfetch/, "測試缺少 runtime fetch 防線");
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
