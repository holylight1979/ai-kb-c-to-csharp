# Constant Value Mixup (值交換/偏移)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-B
> 信心度: VERIFIED
> 前置知識: MERC.H 常數定義
> 相關原子: verification/compare-constants
> 觸發條件: 常數值與 C 原始碼定義不一致

## 知識

移植時常數值可能因手動輸入而發生交換或偏移錯誤。
這類錯誤極為隱蔽，因為程式碼結構看起來完全正確，只有數值不對。

**已知案例：**

```csharp
// 錯誤：GOD_DARK = 3
public const int GOD_DARK = 3;
// 正確：GOD_DARK = 2（C 原始碼中的定義）
public const int GOD_DARK = 2;
```

```csharp
// 錯誤：PULSE_TICK = 60
public const int PULSE_TICK = 60;
// 正確：PULSE_TICK = 92（C 原始碼中的定義）
public const int PULSE_TICK = 92;
```

常見錯誤模式：
- 相鄰常數的值互換（GOD_LIGHT=3, GOD_DARK=2 寫反）
- 數值偏移一位（off-by-one）
- 位元旗標漏掉一個位移（1<<5 寫成 1<<4）
- 十六進位轉十進位時計算錯誤

**高風險區域：**
- PULSE_* 系列（影響遊戲節奏）
- VECT_SECT_* 系列（影響登入/登出判斷）
- GOD_* 系列（影響神明系統邏輯）
- ACT_* / PLR_* 位元旗標（影響角色狀態）

## 行動

1. 執行 compare-constants 工具比對所有常數值
2. 逐一核對 C 原始碼 `#define` 與 C# `const` 的值
3. 特別注意相鄰定義的值是否交換
4. 修正所有不一致的值

## 驗證

```bash
# compare-constants 應顯示 0 個 MISMATCH
python -X utf8 tools/compare-constants.py
# 預期輸出: MISMATCH: 0
```

## 失敗時

→ verification/compare-constants, syntax/merc-h-constants
