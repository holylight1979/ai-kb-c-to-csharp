# Debug Output Left in Code (殘留的除錯輸出)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-O
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: verification/grep-console-write
> 觸發條件: C# 中有 Console.Write 但 C 原始碼無對應 printf

## 知識

移植過程中為了除錯，開發者會加入 Console.Write/Console.WriteLine
來追蹤程式流程。這些輸出在除錯結束後可能忘記移除，殘留在正式碼中。

**典型案例：**

C 原始碼（無 printf）：
```c
void boot_db(void)
{
    load_area_list();
    load_helps();
    fix_exits();
    // 沒有任何 printf/fprintf 到 stdout
}
```

C# 移植（殘留除錯輸出）：
```csharp
public void BootDb()
{
    Console.WriteLine("[DEBUG] Starting BootDb...");  // 不應存在
    LoadAreaList();
    Console.WriteLine("[DEBUG] Areas loaded");        // 不應存在
    LoadHelps();
    Console.WriteLine($"[DEBUG] {helpCount} helps loaded");  // 不應存在
    FixExits();
    Console.WriteLine("[DEBUG] BootDb complete");     // 不應存在
}
```

**合法的輸出 vs 除錯殘留：**

合法（C 中有對應）：
```c
fprintf(stderr, "Fix_exits: %d bad resets", nMatch);
// → C# 中的 Console.Error.WriteLine 是合法的
```

除錯殘留（C 中無對應）：
```csharp
Console.WriteLine("[DEBUG] entering function");   // 移除
Console.Write($"ch.Name = {ch.Name}");            // 移除
System.Diagnostics.Debug.WriteLine("trace");      // 移除
```

**為什麼危險：**
- 效能影響（大量 I/O）
- 洩漏內部資訊到控制台
- 日誌混亂，難以辨識真正的錯誤訊息
- 玩家可能看到除錯資訊

**搜尋模式：**
```
Console.Write
Console.WriteLine
Debug.Write
Debug.WriteLine
Trace.Write
System.Diagnostics
```

## 行動

1. grep 所有 `Console.Write` 出現位置
2. 逐一檢查 C 原始碼是否有對應的 printf/fprintf
3. 移除所有沒有 C 對應的輸出語句
4. 合法的輸出保留但確認格式正確

```bash
grep -rn "Console.Write" {CSHARP_DIR}/MudGM/Src/
```

## 驗證

- `grep -c "Console.Write" {CSHARP_DIR}/MudGM/Src/*.cs` 應回報 0
  （或僅有與 C 原始碼 printf 對應的合法輸出）
- 合法輸出應使用 Logger 而非直接 Console

## 失敗時

→ verification/grep-console-write
