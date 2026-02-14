# Format Width Treated as Arg (printf 寬度格式變成 Format 參數)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-R
> 信心度: VERIFIED
> 前置知識: C printf 格式 vs C# string.Format
> 相關原子: syntax/printf-to-format, patterns/string-format
> 觸發條件: Format 的引數數量與佔位符數量不符

## 知識

C 的 `printf` 和 C# 的 `string.Format` 處理欄位寬度的語法不同。
移植時容易將 C 的寬度修飾符誤當成額外的參數。

**C printf 語法：**
```c
// %3d 表示「至少 3 字元寬，右對齊」
// 只需要一個引數（value）
printf("攻擊力: %3d\n", value);

// %-15s 表示「至少 15 字元寬，左對齊」
printf("名稱: %-15s 等級: %3d\n", name, level);
```

**C# string.Format 語法：**
```csharp
// {0,3} 表示「第 0 個引數，至少 3 字元寬，右對齊」
// {0,-15} 表示「第 0 個引數，至少 15 字元寬，左對齊」
string.Format("攻擊力: {0,3}\n", value);
string.Format("名稱: {0,-15} 等級: {1,3}\n", name, level);
```

**錯誤移植：**
```csharp
// 錯誤：把寬度 3 當成第二個參數
string.Format("攻擊力: {0}{1}\n", value, 3);
// 輸出: "攻擊力: 425 3"（多出一個 "3"）

// 錯誤：寬度在引數列而非佔位符內
string.Format("名稱: {0} 等級: {1}\n", name, 15, level, 3);
// FormatException 或輸出錯亂
```

**正確移植：**
```csharp
// 正確：寬度放在佔位符內
string.Format("攻擊力: {0,3}\n", value);

// 或使用字串插值
$"攻擊力: {value,3}\n";
```

**對照表：**
| C printf | C# Format     | C# 插值          |
|----------|---------------|-------------------|
| `%d`     | `{0}`         | `{value}`         |
| `%3d`    | `{0,3}`       | `{value,3}`       |
| `%-3d`   | `{0,-3}`      | `{value,-3}`      |
| `%03d`   | `{0:D3}`      | `{value:D3}`      |
| `%5.2f`  | `{0,5:F2}`    | `{value,5:F2}`    |
| `%-15s`  | `{0,-15}`     | `{name,-15}`      |

**偵測方法：**
- 計算 Format 呼叫中佔位符數量與引數數量
- 若引數 > 佔位符，可能有寬度被當引數
- 搜尋 `, 3)` 或 `, 15)` 等可疑的數字引數

## 行動

1. 列出所有 `string.Format` 呼叫
2. 比對佔位符數量與引數數量
3. 對照 C 原始碼的 printf 格式
4. 修正寬度語法為 `{N,width}` 格式

## 驗證

- 每個 Format 呼叫的佔位符數 == 引數數
- 輸出字串的對齊格式與 C 一致
- 無 FormatException 風險

## 失敗時

→ syntax/printf-to-format, patterns/string-format
