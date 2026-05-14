#!/usr/bin/env bash
# 從 anthropics/claude-plugins-official 拉取最新 skill-creator 覆蓋本地
# ./update-skill-creator.ps1
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

echo ">>> 完成！skill-creator 已更新至最新版本。"
