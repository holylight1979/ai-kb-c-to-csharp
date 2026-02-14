# Big5 波浪號問題（0x7E）

> 來源: Big5 編碼規格，MUD 區域檔案格式
> 信心度: VERIFIED
> 前置知識: atoms/encoding/big5-what-is.md
> 相關原子: atoms/syntax/fread-string.md, atoms/encoding/0x5C-backslash.md
> 觸發條件: 讀取區域檔案時字串被截斷；fread_string 提前結束

## 知識
部分 Big5 中文字的第二位元組是 0x7E（波浪號 `~`）。
MUD 區域檔案使用 `~` 作為字串結束標記 → 衝突。

### 問題本質
```
fread_string 逐 byte 讀取，遇到 0x7E 就停止。
若中文字 = [前導][0x7E]，fread_string 會在中文字中間停止。
→ 字串被截斷，前導位元組變成孤立 byte → 亂碼
```

### 受影響字元（部分）
```
功能中 0x7E 作為後隨位元組的字較少，但確實存在：
後隨位元組範圍 0x40-0x7E 中，0x7E 是上限
```

### 原始 C 程式碼的處理
多數 Merc 衍生 MUD 的 `fread_string` **沒有**處理此問題：
```c
// 典型的（有漏洞的）fread_string
while ((c = getc(fp)) != '~' && c != EOF) {
    // 直接逐 byte 比較，不考慮 Big5
}
```

### C# 安全實作
```csharp
public static string FreadString(BinaryReader reader, Encoding big5) {
    var bytes = new List<byte>();
    while (true) {
        byte b = reader.ReadByte();
        if (b >= 0x81 && b <= 0xFE) {
            // Big5 前導位元組：必須讀取下一個 byte
            bytes.Add(b);
            byte b2 = reader.ReadByte();
            bytes.Add(b2);
            // 即使 b2 == 0x7E 也不停止
        } else if (b == (byte)'~') {
            break;  // 真正的結束標記
        } else {
            bytes.Add(b);
        }
    }
    return big5.GetString(bytes.ToArray());
}
```

## 行動
- fread_string 必須以 Big5-aware 方式判斷 `~`
- 辨識前導位元組後，後隨位元組不當結束標記
- 測試含 0x7E 後隨位元組的中文字串

## 驗證
- 讀取含 0x7E 字元的區域檔案字串不會截斷
- 完整字串與原始資料 byte-for-byte 一致

## 失敗時
→ atoms/encoding/big5-what-is.md（確認 Big5 位元組結構）
