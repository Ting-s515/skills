import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { after, before, test } from "node:test";
import { buildSite } from "../script/build-site.mjs";

let outputDirectory;
let html;

before(async () => {
  outputDirectory = await mkdtemp(path.join(os.tmpdir(), "k8s-docs-web-"));
  const result = await buildSite({ outputDirectory });
  html = await readFile(path.join(outputDirectory, "index.html"), "utf8");

  assert.equal(result.documentCount, 15);
});

after(async () => {
  await rm(outputDirectory, { recursive: true, force: true });
});

test("將全部教材預先寫入單一靜態 HTML", () => {
  const panels = html.match(/class="document-panel markdown-body"/g) ?? [];

  assert.equal(panels.length, 15);
  assert.match(html, /Lab 00：認識 Kubernetes 的作用與架構/);
  assert.match(html, /Kubernetes kubectl 常用指令速查表/);
  assert.doesNotMatch(html, /\?doc=/);
});

test("將教材間的 Markdown 連結改為同頁 hash", () => {
  assert.match(html, /href="#doc-supplement-local-application"/);
  assert.match(html, /href="#doc-04-kubectl-operation"/);
  assert.match(html, /href="#doc-99-kubectl-command--1-bash-與-context"/);
  assert.doesNotMatch(html, /href="[^"]+\.md(?:#|\")/);
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
