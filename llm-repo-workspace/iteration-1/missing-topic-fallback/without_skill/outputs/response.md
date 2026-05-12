# Rust 的 Ownership（所有權）機制

## 什麼是 Ownership？

Ownership 是 Rust 的核心記憶體管理機制，讓 Rust 不需要垃圾回收器（GC）也能確保記憶體安全。每一個值（value）在 Rust 中都有且只有一個「擁有者」（owner），當擁有者離開作用域（scope）時，該值會被自動釋放。

---

## 三條核心規則

1. **每個值都有一個擁有者（owner）**
2. **同一時間只能有一個擁有者**
3. **當擁有者離開作用域，值會被自動丟棄（drop）**

---

## 移動語義（Move Semantics）

當你將一個值賦值給另一個變數，或傳入函式，所有權會被「移動（move）」，原本的變數就無法再使用。

```rust
let s1 = String::from("hello");
let s2 = s1; // s1 的所有權移動到 s2

// 下面這行會編譯錯誤，因為 s1 已經無效
// println!("{}", s1);
println!("{}", s2); // OK
```

> 注意：基本型別（如整數、浮點數、bool）實作了 `Copy` trait，賦值時是複製而非移動，原變數仍可使用。

---

## 借用（Borrowing）與參考（References）

若不想轉移所有權，可以使用「借用」，即傳遞參考（`&`）：

### 不可變借用（Immutable Borrow）

```rust
let s = String::from("hello");
let len = calculate_length(&s); // 借用 s，不轉移所有權
println!("{} 的長度是 {}", s, len); // s 仍然有效
```

- 同一時間可以有多個不可變借用
- 擁有不可變借用時，原值不能被修改

### 可變借用（Mutable Borrow）

```rust
let mut s = String::from("hello");
change(&mut s); // 可變借用

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}
```

- 同一時間只能有**一個**可變借用
- 有可變借用時，不能同時存在其他借用（可變或不可變）

---

## 生命週期（Lifetimes）

生命週期是 Rust 用來確保借用有效性的機制，防止「懸空參考（dangling reference）」。編譯器的借用檢查器（borrow checker）會自動推斷大多數情況，但在某些複雜場景下需要明確標注：

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

`'a` 是生命週期參數，表示回傳的參考與輸入參考的生命週期相同。

---

## Ownership 解決了什麼問題？

| 問題 | 傳統語言 | Rust 的解法 |
|------|----------|-------------|
| 記憶體洩漏 | GC 或手動 free | 作用域結束自動 drop |
| 雙重釋放（double free） | 執行期錯誤 | 編譯期阻止 |
| 懸空指標（dangling pointer） | 執行期崩潰 | 生命週期檢查 |
| 資料競爭（data race） | 需靠鎖或慣例 | 借用規則在編譯期排除 |

---

## 總結

Rust 的 Ownership 機制透過三個核心概念在**編譯期**保證記憶體安全：

- **所有權（Ownership）**：每個值只有一個擁有者，離開作用域自動釋放
- **借用（Borrowing）**：以參考傳遞值，不轉移所有權，分為可變與不可變
- **生命週期（Lifetimes）**：確保參考在其指向的資料有效期間內使用

這讓 Rust 在不依賴垃圾回收的前提下，達到與 GC 語言相當的記憶體安全性，同時保有 C/C++ 等級的執行效能。
