import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { build } from "esbuild";
import rehypeSlug from "rehype-slug";
import rehypeStringify from "rehype-stringify";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import { unified } from "unified";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const webDirectory = path.resolve(scriptDirectory, "..");
const repositoryDirectory = path.resolve(webDirectory, "..");
const docsDirectory = path.join(repositoryDirectory, "docs");
const sourceDirectory = path.join(webDirectory, "src");
const defaultOutputDirectory = path.join(webDirectory, "dist");

const sectionDefinitions = [
  { key: "core", title: "核心課程" },
  { key: "reference", title: "速查資料" },
  { key: "supplement", title: "選修補充" },
];

function visit(node, callback) {
  callback(node);

  if (Array.isArray(node.children)) {
    for (const child of node.children) {
      visit(child, callback);
    }
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function safeDecodeURIComponent(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function createDocumentId(fileName) {
  return `doc-${fileName
    .replace(/\.md$/i, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")}`;
}

function getSection(fileName) {
  if (fileName.startsWith("supplement-")) {
    return "supplement";
  }

  if (fileName.startsWith("99-")) {
    return "reference";
  }

  return "core";
}

function getTitle(markdown, fileName) {
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim();
  return heading ?? fileName.replace(/\.md$/i, "");
}

function isExternalLink(href) {
  return /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(href);
}

function resolveDocumentLink(href, currentFile, documentIds) {
  if (href.startsWith("#")) {
    return `#${documentIds.get(currentFile)}--${safeDecodeURIComponent(href.slice(1))}`;
  }

  if (isExternalLink(href)) {
    return href;
  }

  const [linkedPath, fragment] = href.split("#", 2);
  const decodedPath = safeDecodeURIComponent(linkedPath).replaceAll("\\", "/");

  if (!decodedPath.toLowerCase().endsWith(".md")) {
    return href;
  }

  const targetFile = path.posix.normalize(
    path.posix.join(path.posix.dirname(currentFile), decodedPath),
  );
  const targetId = documentIds.get(targetFile);

  if (!targetId) {
    return href;
  }

  return fragment
    ? `#${targetId}--${safeDecodeURIComponent(fragment)}`
    : `#${targetId}`;
}

function rehypePrepareStaticDocument(options) {
  const { currentFile, documentIds } = options;
  const currentId = documentIds.get(currentFile);

  return (tree) => {
    visit(tree, (node) => {
      if (node.type !== "element") {
        return;
      }

      node.properties ??= {};

      if (node.properties.id) {
        node.properties.id = `${currentId}--${node.properties.id}`;
      }

      if (node.tagName === "a" && typeof node.properties.href === "string") {
        const href = node.properties.href;
        node.properties.href = resolveDocumentLink(
          href,
          currentFile,
          documentIds,
        );

        if (isExternalLink(href)) {
          node.properties.target = "_blank";
          node.properties.rel = ["noreferrer", "noopener"];
        }
      }

      if (
        node.tagName === "pre" &&
        node.children?.length === 1 &&
        node.children[0].tagName === "code" &&
        node.children[0].properties?.className?.includes("language-mermaid")
      ) {
        const source = node.children[0].children
          .filter((child) => child.type === "text")
          .map((child) => child.value)
          .join("");

        node.tagName = "div";
        node.properties = { className: ["mermaid"] };
        node.children = [{ type: "text", value: source }];
      }
    });
  };
}

async function renderMarkdown(markdown, currentFile, documentIds) {
  const rendered = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, {
      footnoteLabel: "註腳",
      footnoteBackLabel: "返回內容",
    })
    .use(rehypeSlug)
    .use(rehypePrepareStaticDocument, { currentFile, documentIds })
    .use(rehypeStringify)
    .process(markdown);

  return String(rendered);
}

async function readDocuments() {
  const fileNames = (await readdir(docsDirectory))
    .filter((fileName) => fileName.toLowerCase().endsWith(".md"))
    .sort((left, right) => left.localeCompare(right, "zh-Hant"));
  const documentIds = new Map(
    fileNames.map((fileName) => [fileName, createDocumentId(fileName)]),
  );

  return Promise.all(
    fileNames.map(async (fileName) => {
      const markdown = await readFile(path.join(docsDirectory, fileName), "utf8");

      return {
        fileName,
        id: documentIds.get(fileName),
        section: getSection(fileName),
        title: getTitle(markdown, fileName),
        html: await renderMarkdown(markdown, fileName, documentIds),
      };
    }),
  );
}

function renderNavigation(documents) {
  return sectionDefinitions
    .map(({ key, title }) => {
      const links = documents
        .filter((document) => document.section === key)
        .map(
          (document, index) => `
            <li>
              <a class="document-link${key === "core" && index === 0 ? " is-active" : ""}" href="#${document.id}"${key === "core" && index === 0 ? ' aria-current="page"' : ""}>
                <span class="document-title">${escapeHtml(document.title)}</span>
                <span class="document-file">${escapeHtml(document.fileName)}</span>
              </a>
            </li>`,
        )
        .join("");

      return `
        <section class="navigation-section">
          <h2>${title}</h2>
          <ul>${links}
          </ul>
        </section>`;
    })
    .join("");
}

function renderContent(documents) {
  return documents
    .map(
      (document, index) => `
        <article
          class="document-panel markdown-body"
          id="${document.id}"
          data-document-path="${escapeHtml(document.fileName)}"
          aria-label="${escapeHtml(document.title)}"
          ${index === 0 ? "" : "hidden"}
        >
${document.html}
        </article>`,
    )
    .join("");
}

export async function buildSite({ outputDirectory = defaultOutputDirectory } = {}) {
  const documents = await readDocuments();
  const template = await readFile(path.join(sourceDirectory, "index.html"), "utf8");
  const html = template
    .replace("{{DOCUMENT_COUNT}}", String(documents.length))
    .replace("<!-- DOCUMENT_NAVIGATION -->", renderNavigation(documents))
    .replace("<!-- DOCUMENT_CONTENT -->", renderContent(documents));

  await rm(outputDirectory, { recursive: true, force: true });
  await mkdir(outputDirectory, { recursive: true });
  await Promise.all([
    writeFile(path.join(outputDirectory, "index.html"), html, "utf8"),
    readFile(path.join(sourceDirectory, "style.css"), "utf8").then((css) =>
      writeFile(path.join(outputDirectory, "style.css"), css, "utf8"),
    ),
    build({
      entryPoints: [path.join(sourceDirectory, "app.mjs")],
      bundle: true,
      format: "esm",
      target: "es2022",
      minify: true,
      outfile: path.join(outputDirectory, "app.mjs"),
      logLevel: "silent",
    }),
  ]);

  return { documentCount: documents.length, outputDirectory };
}

const invokedFile = process.argv[1] ? pathToFileURL(path.resolve(process.argv[1])).href : "";

if (import.meta.url === invokedFile) {
  const result = await buildSite();
  console.log(
    `已產生 ${result.documentCount} 份教材：${path.join(result.outputDirectory, "index.html")}`,
  );
}
