# Tilde One-Line (fread_string 只讀一行而非讀到波浪號)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-T
> 信心度: VERIFIED
> 前置知識: Merc fread_string 格式, Big5 編碼
> 相關原子: patterns/fread-string, encoding/big5-tilde
> 觸發條件: C# 的字串讀取使用 ReadLine 而非讀到 ~ 終止符

## 知識

Merc/ROM MUD 的區域檔案格式使用波浪號 `~` 作為字串結束標記。
一個字串可以跨越多行，直到遇到獨立的 `~` 才結束。
C# 若使用 `ReadLine()` 只讀一行，多行描述會被截斷。

**C 的 fread_string 行為：**
```c
char *fread_string(FILE *fp)
{
    // 持續讀取直到遇到 '~'
    // 支援多行文字
    // 換行符會保留在字串中
    char c;
    while ((c = getc(fp)) != '~')
    {
        // 累積字元到緩衝區
        // 包含換行符
    }
}
```

**區域檔案範例（多行描述）：**
```
#3001
Name 市集廣場~
Desc
你站在繁忙的市集廣場中央。
四周商販的叫賣聲此起彼落，
空氣中瀰漫著食物的香氣。
北方是城堡的入口，南方通往港口。
~
```

**錯誤 C# 實作（只讀一行）：**
```csharp
public string FreadString(StreamReader reader)
{
    // 錯誤：只讀一行，多行描述被截斷
    string line = reader.ReadLine();
    return line.TrimEnd('~');
    // 只得到 "你站在繁忙的市集廣場中央。"
    // 遺失後面三行描述
}
```

**正確 C# 實作（讀到波浪號）：**
```csharp
public string FreadString(StreamReader reader)
{
    var sb = new StringBuilder();
    int c;
    while ((c = reader.Read()) != -1)
    {
        if ((char)c == '~')
            break;
        sb.Append((char)c);
    }
    return sb.ToString().TrimEnd('\r', '\n');
}
```

**Big5 波浪號陷阱：**
Big5 編碼中，某些中文字的第二位元組是 0x7E（ASCII `~`）。
若逐位元組掃描，可能將中文字的一半誤認為結束標記。
```
例: "盻" 的 Big5 碼 = 0xAC 0x7E
第二位元組 0x7E == '~' 會被誤判為結束！
```

必須追蹤 Big5 雙位元組狀態，在第二位元組時跳過 `~` 檢查。

## 行動

1. 找到 C# 的 FreadString 實作
2. 確認使用逐字元讀取直到 `~`，而非 ReadLine
3. 加入 Big5 雙位元組保護（第二位元組的 0x7E 不是結束標記）
4. 測試多行描述的讀取

## 驗證

- 用含多行描述的測試區域檔案驗證
- 確認所有行都被正確讀取
- 測試含有 Big5 0x7E 第二位元組的字串不會提前截斷

## 失敗時

→ patterns/fread-string, encoding/big5-tilde
