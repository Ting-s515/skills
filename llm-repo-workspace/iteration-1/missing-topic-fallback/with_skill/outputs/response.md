# Rust 的 Ownership 機制

> **wiki 查詢結果：** 已讀取 `index.md`，wiki 知識庫（共 38 頁）中目前沒有 Rust 相關頁面。  
> 以下說明全部來自模型自身知識，非 wiki 資料。

---

## 什麼是 Ownership？

Ownership（所有權）是 Rust 語言的核心記憶體管理機制，目的是在**不需要 Garbage Collector（GC）的情況下**，於編譯期（compile time）保證記憶體安全，避免：

- Use-after-free（釋放後使用）
- Double-free（重複釋放）
- Dangling pointer（懸空指標）
- Data race（多執行緒資料競爭）

---

## 三條核心規則

1. **每個值都有且只有一個 Owner（擁有者）**  
   每個資料在任意時刻只能屬於一個變數（owner）。

2. **Owner 離開作用域時，值自動被釋放**  
   當 owner 的 scope 結束，Rust 自動呼叫 `drop()`，釋放記憶體。

3. **所有權可以「移動」（Move），但一次只能有一個 Owner**  
   將值賦給另一個變數時，原變數的所有權轉移（move），原變數不再有效。

---

## 範例說明

### Move（所有權移轉）

```rust
let s1 = String::from("hello");
let s2 = s1; // s1 的所有權移轉給 s2

// 以下這行會編譯錯誤，因為 s1 已不再有效
// println!("{}", s1);
println!("{}", s2); // OK
```

### Clone（深複製，保留原值）

```rust
let s1 = String::from("hello");
let s2 = s1.clone(); // 明確複製一份新資料

println!("{} and {}", s1, s2); // 兩個都有效
```

### Copy（基本型別自動複製）

```rust
let x = 5;
let y = x; // i32 實作了 Copy trait，x 仍然有效

println!("{} and {}", x, y); // 兩個都有效
```

`i32`、`bool`、`f64`、`char` 等儲存在 Stack 的基本型別，預設實作 `Copy`，賦值時是複製而非移轉。

---

## Borrowing（借用）

為了讓多個地方能使用同一個值，Rust 提供「借用（Borrow）」機制，使用 `&` 符號：

### 不可變借用（Immutable Reference）

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
} // s 離開作用域，但不釋放，因為它不是 owner

let s1 = String::from("hello");
let len = calculate_length(&s1);
println!("'{}' 的長度是 {}", s1, len); // s1 仍然有效
```

### 可變借用（Mutable Reference）

```rust
fn change(s: &mut String) {
    s.push_str(", world");
}

let mut s = String::from("hello");
change(&mut s);
println!("{}", s); // "hello, world"
```

**可變借用的限制：**
- 同一時刻，對同一個值只能有**一個**可變借用
- 可變借用與不可變借用**不能同時存在**

這些限制由編譯器的 **Borrow Checker** 在編譯期強制執行。

---

## Lifetime（生命週期）

當借用橫跨函式邊界時，Rust 需要確保被借用的值在借用存活期間內不會被釋放。這就是 **Lifetime 標註**的用途：

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

`'a` 告訴編譯器：回傳的 reference 的生命週期與 x、y 中較短的那個相同。

---

## 總結

| 概念 | 說明 |
|------|------|
| Ownership | 每個值只有一個 owner，owner 離開 scope 即釋放 |
| Move | 所有權轉移後，原變數失效 |
| Clone | 明確深複製，兩份都有效 |
| Copy | 基本型別自動複製，無 move 語意 |
| Borrow (`&`) | 暫時借用，不取得所有權 |
| Mutable Borrow (`&mut`) | 可修改，同時只能有一個 |
| Lifetime | 確保 reference 不會比被借用的值活得更久 |

Rust 的 Ownership 機制讓記憶體管理在編譯期完成，執行期完全不需要 GC，達到與 C/C++ 相當的效能，同時具備記憶體安全保證。

---

> **補充說明：** 以上內容為模型自身知識補充，wiki 知識庫目前無 Rust 相關頁面。若需要將 Rust Ownership 加入 wiki，可請使用者建立對應頁面。
