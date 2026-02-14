# 巨集轉方法

> 來源: MERC.H, 大量 #define 巨集
> 信心度: VERIFIED
> 前置知識: atoms/syntax/pointer-deref.md
> 相關原子: 無
> 觸發條件: 看到 C 的 #define 巨集（帶參數）

## 知識
C 的 `#define` 巨集在 C# 中通常轉為 `static` 方法或屬性。

### 簡單判斷巨集 → 靜態方法
```c
#define IS_AWAKE(ch)       (ch->position > POS_SLEEPING)
#define IS_NPC(ch)         (IS_SET(ch->act, ACT_IS_NPC))
#define IS_IMMORTAL(ch)    (get_trust(ch) >= LEVEL_IMMORTAL)
#define GET_AC(ch)         ((ch)->armor)
```
```csharp
public static bool IsAwake(CharData ch) => ch.Position > POS_SLEEPING;
public static bool IsNpc(CharData ch) => IsSet(ch.Act, ACT_IS_NPC);
public static bool IsImmortal(CharData ch) => GetTrust(ch) >= LEVEL_IMMORTAL;
public static int GetAc(CharData ch) => ch.Armor;
```

### 位元操作巨集 → 靜態方法
```c
#define IS_SET(flag, bit)    ((flag) & (bit))
#define SET_BIT(var, bit)    ((var) |= (bit))
#define REMOVE_BIT(var, bit) ((var) &= ~(bit))
```
```csharp
public static bool IsSet(long flag, long bit) => (flag & bit) != 0;
public static void SetBit(ref long var, long bit) => var |= bit;
public static void RemoveBit(ref long var, long bit) => var &= ~bit;
```

### 常數巨集 → const 或 static readonly
```c
#define MAX_LEVEL    60
#define MAX_STRING   4096
```
```csharp
public const int MAX_LEVEL = 60;
public const int MAX_STRING = 4096;
```

注意事項：
- 巨集的多次展開副作用（如 `MAX(a++, b++)`）在方法中自動消失
- 確保語意完全保留，特別是 IS_SET 回傳型別（C 是 int，C# 是 bool）

## 行動
- 判斷巨集 → `static bool` 方法，expression body
- 修改巨集 → `static void` 方法，參數加 `ref`
- 常數巨集 → `const` 或 `static readonly`
- 方法名 PascalCase

## 驗證
- 所有巨集呼叫處已替換為方法呼叫
- IS_SET 回傳 bool，不再作為 int 使用

## 失敗時
→ 檢查巨集原始定義，確認展開後的完整語意
