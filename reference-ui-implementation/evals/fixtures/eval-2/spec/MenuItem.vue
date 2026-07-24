<script setup lang="ts">
defineProps<{
  href: string
  label: string
}>()
</script>

<template>
  <div class="menu-item-shell">
    <li class="menu-item">
      <a class="menu-link" :href="href">{{ label }}</a>
    </li>
  </div>
</template>
