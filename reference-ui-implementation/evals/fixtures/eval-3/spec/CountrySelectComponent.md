# `app-country-select` 實際 render DOM

Angular 共用元件 `app-country-select` 最終會產生以下 DOM：

```html
<app-country-select>
  <div class="country-select-shell">
    <select class="country-select" name="country">
      <option value="tw">Taiwan</option>
      <option value="jp">Japan</option>
    </select>
  </div>
</app-country-select>
```

元件無法關閉 host element，也無法移除 `country-select-shell` wrapper。
