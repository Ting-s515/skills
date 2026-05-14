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
git sparse-checkout set "$SKILL_PATH" --quiet

echo ">>> 覆蓋本地 $TARGET_DIR ..."
cp -r "$SKILL_PATH/." "$TARGET_DIR/"

cd ~
rm -rf "$TMP_DIR"

echo ">>> 完成！skill-creator 已更新至最新版本。"
