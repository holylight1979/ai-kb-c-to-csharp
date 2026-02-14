# Big5 反斜線問題（0x5C）

> 來源: Big5 編碼規格，移植實戰經驗
> 信心度: VERIFIED
> 前置知識: atoms/encoding/big5-what-is.md
> 相關原子: atoms/encoding/corruption-model.md
> 觸發條件: 中文字串在非 Big5 感知工具中出現亂碼或截斷

## 知識
85+ 個常用 Big5 中文字的第二位元組是 0x5C（反斜線 `\`）。

### 問題本質
Big5 字元 = [前導][後隨]，當後隨位元組 = 0x5C 時：
- 不了解 Big5 的工具會把 0x5C 當成 `\`（跳脫字元）
- 接下來的位元組被當成跳脫序列的一部分 → 整個字串損壞

### 受影響的常見字（部分）
```
功 = A5 5C    許 = B3 5C    能 = 能 (ok, not 5C)
拆 = A8 5C    粗 = B2 5C    龜 = C0 5C
房 = A8 5C    設 = B3 5C    軟 = B3 5C
```

### 損壞範例
```
原始 Big5: A5 5C B3 5C ("功許")
損壞解讀: A5 [5C=\] B3 [5C=\] → 跳脫處理 → 亂碼
```

### 安全處理策略
1. **永遠用 Big5-aware 方式解碼**（先完整解碼，再處理文字）
2. **不要** byte-by-byte 處理 Big5 字串
3. 正則表達式必須在解碼後的 Unicode 字串上操作
4. 序列化/反序列化時注意 JSON 的 `\` 跳脫

### C# 安全做法
```csharp
// 安全：先完整解碼
var enc = Encoding.GetEncoding(950);
string text = enc.GetString(rawBytes);  // 整塊解碼
// 之後只操作 string，不碰 bytes

// 危險：逐 byte 處理
// NEVER: for (int i=0; i<bytes.Length; i++) if (bytes[i] == '\\') ...
```

## 行動
- 確保所有 Big5 處理都是整塊解碼而非逐 byte
- 搜尋 byte-level 字串處理程式碼，改為 encoding-aware

## 驗證
- 含 0x5C 後隨位元組的中文字能正確顯示
- 「功」「許」「設」等字不會在處理過程中損壞

## 失敗時
→ atoms/encoding/corruption-model.md（損壞模型與修復）
