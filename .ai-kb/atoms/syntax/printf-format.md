# Printf 格式轉換

> 來源: COMM.C, ACT_*.C, 通用 C→C# 移植慣例
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/format-width-fatal.md, atoms/cstr/format-conversion.md
> 觸發條件: 看到 C 的 sprintf/printf/fprintf 呼叫

## 知識
C printf 格式字串對應 C# string.Format：

| C 格式   | C# 格式      | 說明                |
|----------|-------------|---------------------|
| `%d`     | `{N}`       | 整數                |
| `%s`     | `{N}`       | 字串                |
| `%3d`    | `{N,3}`     | 右對齊寬度 3        |
| `%-10s`  | `{N,-10}`   | 左對齊寬度 10       |
| `%02d`   | `{N:D2}`    | 零填充 2 位         |
| `%ld`    | `{N}`       | C# int/long 自動    |
| `%f`     | `{N:F}`     | 浮點數              |
| `%.2f`   | `{N:F2}`    | 小數 2 位           |
| `%%`     | `%`         | 字面百分號          |

完整範例：
```c
sprintf(buf, "%s hits %s for %d damage.", attacker, victim, dam);
```
```csharp
var buf = string.Format("{0} hits {1} for {2} damage.", attacker, victim, dam);
// 或用插值：
var buf = $"{attacker} hits {victim} for {dam} damage.";
```

多行 sprintf 累加（strcat 模式）→ StringBuilder：
```csharp
var sb = new StringBuilder();
sb.AppendFormat("{0,3} {1,-12} {2}\n", num, name, desc);
```

## 行動
- 以 `{N}` 從 0 開始依序替換每個 `%` 佔位符
- 寬度修飾符放在逗號後：`{N,width}`
- 格式修飾符放在冒號後：`{N:format}`
- **絕對不要**把寬度當成額外參數傳入

## 驗證
- 輸出字串與 C 版在相同輸入下完全一致
- 對齊、填充、精度皆正確

## 失敗時
→ atoms/syntax/format-width-fatal.md（寬度參數致命錯誤）
