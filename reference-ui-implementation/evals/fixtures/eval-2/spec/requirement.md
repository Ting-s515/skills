# Vue 實作需求

- 建立 Vue 3 `MenuList.vue`，使用 `<script setup lang="ts">`。
- 接收 `items: Array<{ id: string; href: string; label: string }>`，以 `v-for` 輸出清單。
- 專案已有 `MenuItem.vue`，只有在其實際 render DOM 與參考 markup 相容時才能使用。
- 我明確確認這次可以修改 global CSS：只將
  `.menu > .menu-item + .menu-item` 的 `margin-top` 從 `4px` 改成 `8px`。
- global CSS 的授權不包含 DOM 結構修改，也不可新增其他 CSS 規則或 component style block。
