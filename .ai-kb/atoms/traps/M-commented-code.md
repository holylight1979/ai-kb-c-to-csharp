# Commented Code Ported as Active (註解內的程式碼被當成有效程式碼移植)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-M
> 信心度: VERIFIED
> 前置知識: C 註解語法, Big5 編碼
> 相關原子: encoding/cp950-decode, syntax/c-comments
> 觸發條件: C 中被 /* */ 包圍的程式碼在 C# 中變成有效程式碼

## 知識

C 原始碼中有些條目被 `/* */` 註解掉（表示已廢棄或測試中）。
由於 Big5 編碼的亂碼干擾，AI 模型可能無法正確辨識註解邊界，
將註解內的程式碼當作有效程式碼移植。

**典型案例：技能表中的註解條目**

C 原始碼（Big5 編碼，部分條目被註解）：
```c
const struct skill_type skill_table[] =
{
    { "sword",    spell_null, ... },
/*  { "spells",   spell_null, ... },  */   // 被註解掉！
    { "axe",      spell_null, ... },
};
```

錯誤移植（註解條目變成有效）：
```csharp
new SkillType("sword", SpellNull, ...),
new SkillType("spells", SpellNull, ...),  // 不應存在！
new SkillType("axe", SpellNull, ...),
```

**為什麼會發生：**
- Big5 亂碼中 `/*` 和 `*/` 標記不明顯
- AI 模型專注於「結構」而忽略註解邊界
- 長陣列中的單一註解行容易被忽略
- 有些註解跨多行，更難追蹤

**影響：**
- 技能表多出額外條目（MAX_SKILL 不匹配）
- 法術表有不應存在的法術
- 指令表有廢棄的指令被啟用
- 陣列索引偏移（後續條目全部錯位）

**其他容易出問題的表格：**
- `skill_table[]` — 技能定義
- `cmd_table[]` — 指令定義
- `spell_table[]` — 法術定義
- `social_table[]` — 社交指令

## 行動

1. 用 `cp950` 解碼 C 原始碼查看完整內容
2. 仔細辨識 `/* */` 和 `//` 的註解邊界
3. 確認所有被註解的條目在 C# 中也是註解或已移除
4. 比對陣列長度與 MAX_* 常數是否一致

## 驗證

- 比對 C 與 C# 的陣列條目數量
- 用 decode-big5 確認每個條目的註解狀態
- 確認 MAX_SKILL 等常數與實際條目數一致

## 失敗時

→ encoding/cp950-decode, syntax/c-comments
