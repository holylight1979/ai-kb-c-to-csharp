# Format 寬度致命錯誤

> 來源: 移植實戰經驗，多次發生
> 信心度: VERIFIED
> 前置知識: atoms/syntax/printf-format.md
> 相關原子: atoms/cstr/format-conversion.md
> 觸發條件: 轉換含寬度修飾符的 printf 格式字串時

## 知識
**致命錯誤**：把 C 的寬度修飾符當成 string.Format 的額外參數。

C 原始碼：
```c
sprintf(buf, "%3d", value);
```

**錯誤轉換**（會造成邏輯錯誤且不報編譯錯誤）：
```csharp
// BAD — 3 變成第二個參數，輸出 "42 3" 而非 " 42"
string.Format("{0} {1}", value, 3);
```

**正確轉換**：
```csharp
// GOOD — 寬度放在逗號後，是佔位符的一部分
string.Format("{0,3}", value);
```

更多易錯範例：
```c
sprintf(buf, "%-15s %3d", name, level);
```
```csharp
// BAD
string.Format("{0} {1} {2} {3}", name, 15, level, 3);
// GOOD
string.Format("{0,-15} {1,3}", name, level);
```

此錯誤特別危險因為：
1. 編譯不會報錯
2. 輸出看起來「差不多」但對齊全亂
3. 參數索引全部偏移 → 後續欄位全錯

## 行動
- 轉換 printf 時，寬度永遠寫在 `{N,width}` 裡
- Code review 時特別檢查所有含數字的 Format 呼叫
- 搜尋 `Format("` 後跟大量參數的行

## 驗證
- 比對 C 版與 C# 版輸出的實際寬度
- 確認 Format 參數數量 = 佔位符數量（不含寬度）

## 失敗時
→ atoms/syntax/printf-format.md（重新理解格式對應）
