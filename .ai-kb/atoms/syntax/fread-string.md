# fread_string 轉換

> 來源: DB.C, 區域檔案格式
> 信心度: VERIFIED
> 前置知識: atoms/encoding/0x7E-tilde.md
> 相關原子: atoms/encoding/big5-what-is.md
> 觸發條件: 移植 DB.C 的檔案讀取函式或處理區域檔案

## 知識
MUD 區域檔案使用 `~`（波浪號，0x7E）作為字串結束標記。

### C 版 fread_string 行為
```c
char *fread_string(FILE *fp) {
    // 1. 跳過前導空白
    // 2. 讀取字元直到遇到 '~'
    // 3. 支援多行（\n 保留在字串中）
    // 4. 回傳 str_dup 的結果
}
```

### C# 實作要點
```csharp
public static string FreadString(StreamReader fp) {
    var sb = new StringBuilder();
    // 跳過前導空白
    SkipWhitespace(fp);
    int c;
    while ((c = fp.Read()) != -1) {
        if (c == '~') break;
        sb.Append((char)c);
    }
    return sb.ToString().TrimEnd();
}
```

### 重要陷阱：Big5 的 0x7E 問題
某些 Big5 中文字的第二位元組是 0x7E（波浪號）：
- 若用 byte-level 讀取，會誤將中文字元的一半當作結束標記
- **必須**用 Big5-aware 方式讀取，或先完整解碼再找 `~`
- 安全做法：以 `Encoding.GetEncoding(950)` 開啟 StreamReader

### fread_string2 變體
```c
char *fread_string2(FILE *fp) {
    // 同上，但額外去除前導空白行
}
```

## 行動
- 實作 FreadString 方法，以 `~` 為結束標記
- 使用 Encoding.GetEncoding(950) 開啟區域檔案
- 測試含中文的多行字串讀取

## 驗證
- 能正確讀取含 `~` 第二位元組的中文字串
- 多行字串保留換行
- 與 C 版讀取結果 byte-for-byte 一致

## 失敗時
→ atoms/encoding/0x7E-tilde.md（波浪號編碼問題）
