# CStr 格式字串轉換

> 來源: CStr.cs 格式化字串慣例
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md, atoms/syntax/printf-format.md
> 相關原子: atoms/syntax/format-width-fatal.md
> 觸發條件: 將含變數的中文字串提取到 CStr

## 知識
含變數的字串（插值或格式化）需要特殊處理。

### 插值字串 → string.Format + CStr
```csharp
// 原始（硬編碼插值）
SendToChar($"{ch.Name} 獲得了 {gold} 金幣。\n", ch);

// 步驟一：提取模板到 CStr
// CStr.cs 中：
public const string ACT_055 = "{0} 獲得了 {1} 金幣。\n";

// 步驟二：使用 string.Format
SendToChar(string.Format(CStr.ACT_055, ch.Name, gold), ch);
```

### 多參數範例
```csharp
// 原始
var msg = $"{attacker.Name} 對 {victim.Name} 造成 {damage} 點傷害！\n";

// CStr.cs:
public const string FIGHT_042 = "{0} 對 {1} 造成 {2} 點傷害！\n";

// 使用：
var msg = string.Format(CStr.FIGHT_042, attacker.Name, victim.Name, damage);
```

### 含寬度/格式的模板
```csharp
// 原始
var line = string.Format("{0,-15} {1,5} {2}", name, level, title);

// 若含中文描述部分：
// CStr.cs: 只提取固定文字部分
public const string AINFO_010 = "名稱            等級 稱號\n";
// 格式模板若只有佔位符不含中文 → 不需要提取
```

### 條件字串
```csharp
// 原始
SendToChar(isDay ? "現在是白天。\n" : "現在是夜晚。\n", ch);

// CStr.cs:
public const string AINFO_020 = "現在是白天。\n";
public const string AINFO_021 = "現在是夜晚。\n";

// 使用：
SendToChar(isDay ? CStr.AINFO_020 : CStr.AINFO_021, ch);
```

### 工具處理
`cstr_replacer.py` 自動偵測插值字串並轉換：
- `$"text {var} text"` → `string.Format(CStr.XXX, var)`
- 保留 `{N}` 佔位符在 CStr 值中
- 參數順序由出現順序決定

## 行動
- 插值字串：提取文字部分，變數改為 `{N}` 佔位符
- 呼叫處改用 `string.Format(CStr.XXX, args...)`
- 確認參數順序與佔位符編號對應

## 驗證
- 格式化輸出與原始版本完全一致
- 參數數量與佔位符數量匹配
- `dotnet build` 編譯通過

## 失敗時
→ atoms/syntax/printf-format.md（格式字串基礎）
→ atoms/syntax/format-width-fatal.md（寬度陷阱）
