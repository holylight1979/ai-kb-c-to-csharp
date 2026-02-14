# Null Terminator Crash ([0]=='\0' 在空字串時崩潰)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-P
> 信心度: VERIFIED
> 前置知識: C 字串 vs C# 字串差異
> 相關原子: syntax/c-string-semantics, patterns/empty-string-check
> 觸發條件: C# 程式碼使用 [0]=='\0' 檢查空字串

## 知識

C 語言中，字串是以 null 結尾的字元陣列。即使是空字串 `""`，
其第一個位元組也是 `'\0'`，所以 `str[0] == '\0'` 是安全的。
但在 C# 中，空字串 `""` 的 Length 為 0，存取 `[0]` 會拋出
`IndexOutOfRangeException`。

**C 的安全寫法：**
```c
// C 中這是安全的，因為 "" 仍有 str[0] == '\0'
if (argument[0] == '\0')
{
    send_to_char("語法錯誤。\n", ch);
    return;
}

// 甚至 NULL 指標也常見
if (str == NULL || str[0] == '\0')
    return;
```

**C# 的錯誤直譯：**
```csharp
// 危險：若 argument 是 "" 或 null，會崩潰！
if (argument[0] == '\0')
{
    ch.SendToChar("語法錯誤。\n");
    return;
}
```

**C# 的正確寫法：**
```csharp
// 方法一：使用 Length 檢查
if (argument.Length == 0)

// 方法二：使用 string.IsNullOrEmpty（推薦）
if (string.IsNullOrEmpty(argument))

// 方法三：若確實需要檢查第一個字元
if (argument.Length == 0 || argument[0] == '\0')
```

**其他相關的 C 字串慣用法：**
```c
// C: 檢查字串是否只有空白
while (isspace(*str)) str++;
if (*str == '\0') ...

// C: 逐字元走訪
for (p = str; *p != '\0'; p++)

// 這些都不能直接用 [index] 在 C# 中直譯
```

**高風險位置：**
- 指令解析（argument 常為空）
- fread 函式（讀取可能回傳空字串）
- 玩家輸入處理（空輸入很常見）

## 行動

1. grep 所有 `[0] == '\0'` 和 `[0] == '\\0'` 的出現位置
2. 替換為 `.Length == 0` 或 `string.IsNullOrEmpty()`
3. 檢查所有字串索引存取前是否有長度檢查
4. 特別注意 null 的情況（C 的 NULL vs C# 的 null）

```bash
grep -rn "\[0\]" {CSHARP_DIR}/MudGM/Src/ | grep -i "null\|\\\\0\|==\s*'"
```

## 驗證

- grep `[0]==` 模式，確認所有字串存取都有保護
- 特別測試空字串和 null 輸入的情況
- 確認無 IndexOutOfRangeException 風險

## 失敗時

→ syntax/c-string-semantics, patterns/empty-string-check
