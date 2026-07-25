import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { after, before, test } from "node:test";
import { buildSite, createDocumentId } from "../script/build-site.mjs";
import { closeDialogOnEscape } from "../src/dialog-keydown.mjs";

let fixtureDirectory;
let outputDirectory;
let html;
const fixtureDocuments = new Map([
  [
    "入門.md",
    "# 入門指南\n\n入門內容唯一標記。\n\n請閱讀 [進階課程](進階.MD#操作流程)。\n",
  ],
  ["進階.MD", "# 進階指南\n\n## 操作流程\n\n進階內容唯一標記。\n"],
  ["A+B.md", "# 加號課程\n\n加號檔名內容。\n"],
  ["A B.md", "# 空白課程\n\n空白檔名內容。\n"],
  ["é.md", "# Composed Unicode\n\nComposed 內容。\n"],
  ["é.md", "# Decomposed Unicode\n\nDecomposed 內容。\n"],
]);

function escapeHtmlAttribute(value) {
  // 測試依實際檔名驗證輸出，因此需套用與 HTML attribute 相同的 escaping。
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

before(async () => {
  fixtureDirectory = await mkdtemp(path.join(os.tmpdir(), "static-docs-web-"));
  const docsDirectory = path.join(fixtureDirectory, "docs");
  outputDirectory = path.join(fixtureDirectory, "dist");
  await mkdir(docsDirectory);
  await Promise.all(
    [...fixtureDocuments].map(([fileName, markdown]) =>
      writeFile(path.join(docsDirectory, fileName), markdown, "utf8"),
    ),
  );

  const result = await buildSite({
    docsDirectory,
    outputDirectory,
    siteMetadata: {
      name: "示例專案",
      title: "示例專案教材",
      description: "示例專案的測試教材網站",
    },
  });
  html = await readFile(path.join(outputDirectory, "index.html"), "utf8");

  assert.equal(result.documentCount, fixtureDocuments.size);
});

after(async () => {
  await rm(fixtureDirectory, { recursive: true, force: true });
});

test("將全部教材預先寫入單一靜態 HTML", () => {
  const panels = html.match(/class="document-panel markdown-body"/g) ?? [];

  assert.equal(panels.length, fixtureDocuments.size);
  for (const [fileName, markdown] of fixtureDocuments) {
    assert.ok(html.includes(`data-document-path="${escapeHtmlAttribute(fileName)}"`));
    const contentMarker = markdown.match(/[^#\s][^\n]*內容[^\n]*/)?.[0];
    assert.ok(contentMarker && html.includes(contentMarker));
  }
  assert.match(html, /<title>示例專案教材<\/title>/);
  assert.doesNotMatch(html, /{{SITE_(?:NAME|TITLE|DESCRIPTION)}}/);
  assert.doesNotMatch(html, /\?doc=/);
});

test("將教材間的 Markdown 連結改為同頁 hash", () => {
  const targetId = createDocumentId("進階.MD");

  assert.ok(html.includes(`href="#${targetId}--操作流程"`));
  assert.doesNotMatch(html, /href="[^"]+\.md(?:#|\")/i);
});

test("為相似與非 ASCII 檔名建立唯一文件 ID", () => {
  const articleIds = [...html.matchAll(/<article[\s\S]*?\bid="([^"]+)"/g)].map(
    (match) => match[1],
  );
  const activeLinks = html.match(/class="document-link is-active"/g) ?? [];
  const currentPages = html.match(/aria-current="page"/g) ?? [];

  assert.equal(articleIds.length, fixtureDocuments.size);
  assert.equal(new Set(articleIds).size, fixtureDocuments.size);
  assert.notEqual(createDocumentId("A+B.md"), createDocumentId("A B.md"));
  assert.notEqual(createDocumentId("入門.md"), createDocumentId("進階.MD"));
  assert.notEqual(createDocumentId("é.md"), createDocumentId("é.md"));
  assert.equal(activeLinks.length, 1);
  assert.equal(currentPages.length, 1);
});

test("輸出瀏覽器所需的靜態資產", async () => {
  const app = await stat(path.join(outputDirectory, "app.mjs"));
  const style = await stat(path.join(outputDirectory, "style.css"));

  assert.ok(app.size > 0);
  assert.ok(style.size > 0);
  assert.doesNotMatch(html, /\/src\//);
});

test("切換文件時只操作既有 DOM，不重新取得 Markdown", async () => {
  const source = await readFile(new URL("../src/app.mjs", import.meta.url), "utf8");

  assert.match(source, /window\.addEventListener\("hashchange"/);
  assert.match(source, /panel\.hidden = panel !== activePanel/);
  assert.doesNotMatch(source, /\bfetch\s*\(/);
});

test("提供 Mermaid 全螢幕縮放與拖曳閱讀器", async () => {
  const source = await readFile(new URL("../src/app.mjs", import.meta.url), "utf8");
  const style = await readFile(new URL("../src/style.css", import.meta.url), "utf8");

  assert.match(html, /id="diagram-dialog"/);
  assert.match(html, /data-diagram-action="zoom-in"/);
  assert.match(source, /button\.className = "diagram-zoom-button"/);
  assert.match(source, /dialog\.showModal\(\)/);
  assert.match(source, /addEventListener\(\s*"wheel"/);
  assert.match(source, /addEventListener\("pointermove"/);
  assert.match(style, /\.diagram-dialog::backdrop/);
  assert.match(style, /\.mermaid-frame\s*{[^}]*width: 100%;/s);
  assert.doesNotMatch(style, /calc\(100vw - 320px/);
});

test("GivenMermaidDialogOpen_WhenPressEscape_ShouldPreventDefaultAndClose", () => {
  let prevented = false;
  let closeCount = 0;
  const event = {
    key: "Escape",
    preventDefault() {
      prevented = true;
    },
  };
  const targetDialog = {
    close() {
      closeCount += 1;
    },
  };

  const handled = closeDialogOnEscape(event, targetDialog);

  assert.equal(handled, true);
  assert.equal(prevented, true);
  assert.equal(closeCount, 1);
});

test("GivenMermaidDialogOpen_WhenPressNonEscape_ShouldRemainOpen", () => {
  const event = {
    key: "Enter",
    preventDefault() {
      assert.fail("非 Escape 鍵不應取消預設行為");
    },
  };
  const targetDialog = {
    close() {
      assert.fail("非 Escape 鍵不應關閉 dialog");
    },
  };

  const handled = closeDialogOnEscape(event, targetDialog);

  assert.equal(handled, false);
});
