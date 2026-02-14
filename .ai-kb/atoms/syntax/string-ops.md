# 字串操作轉換

> 來源: MERC.H, HANDLER.C, 全專案通用
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/null-terminator.md, atoms/syntax/printf-format.md
> 觸發條件: 看到 C 的字串比較/複製/串接/長度函式

## 知識
MUD 原始碼常見字串函式對應表：

### 比較
```c
str_cmp(a, b)       →  !a.Equals(b, StringComparison.OrdinalIgnoreCase)
!str_cmp(a, b)      →  a.Equals(b, StringComparison.OrdinalIgnoreCase)
str_prefix(a, b)    →  b.StartsWith(a, StringComparison.OrdinalIgnoreCase)
!str_prefix(a, b)   →  b.StartsWith(a, StringComparison.OrdinalIgnoreCase)
strcmp(a, b) == 0    →  a == b  // 或 string.Equals(a, b)
```

**注意**：`str_cmp` 回傳 0 表示相等（像 strcmp），所以 `!str_cmp` = 相等。
`str_prefix` 同理，回傳 0 表示匹配，`!str_prefix` = 匹配成功。

### 複製與串接
```c
strcpy(dst, src)    →  dst = src;
strcat(buf, text)   →  buf += text;  // 或 sb.Append(text)
strncpy(d, s, n)    →  d = s.Substring(0, Math.Min(n, s.Length));
```

### 長度與搜尋
```c
strlen(s)           →  s.Length
strstr(hay, needle) →  hay.Contains(needle)  // 或 .IndexOf()
strchr(s, c)        →  s.IndexOf(c)
```

### 特殊 MUD 函式
```c
one_argument(arg, first) →  (first, arg) = OneArgument(arg);
smash_tilde(str)         →  str.Replace('~', '-');
capitalize(str)          →  Capitalize(str)  // 自訂方法
```

## 行動
- 逐一替換每個字串函式呼叫
- 特別注意 `!str_cmp` 的否定語意反轉
- 大量 strcat → 考慮用 StringBuilder

## 驗證
- 大小寫不敏感比較行為一致
- 前綴匹配的參數順序正確（str_prefix 的 a 是前綴）

## 失敗時
→ 檢查原始 C 函式定義確認參數順序與回傳值語意
