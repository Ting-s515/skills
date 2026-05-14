#!/usr/bin/env bash
# 從 anthropics/claude-plugins-official 拉取最新 skill-creator 覆蓋本地

set -e

REPO_URL="https://github.com/anthropics/claude-plugins-official.git"
SKILL_PATH="plugins/skill-creator/skills/skill-creator"
TARGET_DIR="$HOME/.claude/skills/skill-creator"
TMP_DIR=$(mktemp -d)

echo ">>> 拉取最新 skill-creator..."

git clone --depth=1 --filter=blob:none --sparse "$REPO_URL" "$TMP_DIR" --quiet
cd "$TMP_DIR"
git sparse-checkout set "$SKILL_PATH"

echo ">>> 覆蓋本地 $TARGET_DIR ..."

# 備份 evals 目錄（本地自定義，不覆蓋）
EVALS_BACKUP=$(mktemp -d)
[ -d "$TARGET_DIR/evals" ] && cp -r "$TARGET_DIR/evals/." "$EVALS_BACKUP/"

# 清除舊內容（避免殘留過期檔案）
rm -rf "${TARGET_DIR:?}"/{agents,assets,eval-viewer,references,scripts,LICENSE.txt,SKILL.md}

# 複製官方最新內容
cp -r "$SKILL_PATH/." "$TARGET_DIR/"

# 還原 evals 目錄
rm -rf "$TARGET_DIR/evals"
mkdir -p "$TARGET_DIR/evals/files"
[ "$(ls -A "$EVALS_BACKUP" 2>/dev/null)" ] && cp -r "$EVALS_BACKUP/." "$TARGET_DIR/evals/"

cd ~
rm -rf "$TMP_DIR" "$EVALS_BACKUP"

# 套用本地擴充（evals/local_extensions.md「## 插入內容」之後 → 插入 SKILL.md 錨點之後）
LOCAL_EXT="$TARGET_DIR/evals/local_extensions.md"
if [ -f "$LOCAL_EXT" ]; then
    SKILL_MD="$TARGET_DIR/SKILL.md"
    INSERT_TMP=$(mktemp)
    awk '
        BEGIN { found_sep = 0 }
        /^## / {
            line = $0
            sub(/\r$/, "", line)
            if (line == "## 插入內容") {
                found_sep = 1
                next
            }
        }
        found_sep { print }
    ' "$LOCAL_EXT" > "$INSERT_TMP"

    if [ ! -s "$INSERT_TMP" ]; then
        rm -f "$INSERT_TMP"
        echo "Error: 找不到 local_extensions.md 的「## 插入內容」區塊，無法套用本地擴充。" >&2
        exit 1
    fi

    if ! grep -q 'references/schemas\.md.*for the full schema' "$SKILL_MD"; then
        echo "Error: 找不到 SKILL.md 錨點，無法套用本地擴充。" >&2
        exit 1
    fi

    awk -v insertfile="$INSERT_TMP" '
        /references\/schemas\.md.*for the full schema/ {
            print
            while ((getline line < insertfile) > 0) {
                print line
            }
            close(insertfile)
            next
        }
        { print }
    ' "$SKILL_MD" > "$SKILL_MD.tmp" && mv "$SKILL_MD.tmp" "$SKILL_MD"

    rm -f "$INSERT_TMP"
    if ! grep -q 'evals/run_evals\.sh' "$SKILL_MD"; then
        echo "Error: 本地擴充未成功插入 SKILL.md。" >&2
        exit 1
    fi
    if ! grep -q '本地規則：Codex eval runner' "$SKILL_MD"; then
        echo "Error: 本地擴充缺少 Codex eval runner 本地規則。" >&2
        exit 1
    fi
    if ! grep -q -- '--dangerously-bypass-approvals-and-sandbox' "$SKILL_MD"; then
        echo "Error: 本地擴充缺少 Codex bypass sandbox 參數。" >&2
        exit 1
    fi
    echo ">>> 已套用本地擴充 (local_extensions.md)"
fi

echo ">>> 完成！skill-creator 已更新至最新版本。"
