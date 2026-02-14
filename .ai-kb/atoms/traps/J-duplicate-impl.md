# Duplicate Implementation (同一函式在兩個類別中重複實作)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-J
> 信心度: VERIFIED
> 前置知識: C# partial class 架構
> 相關原子: patterns/partial-class, verification/grep-existing
> 觸發條件: 同名函式出現在不同的 partial class 檔案中

## 知識

本專案使用 partial class 將大型 C 檔案拆分為多個 C# 檔案。
這使得同一個函式可能在不同檔案中被重複實作，導致編譯錯誤
或（更危險地）兩個版本行為不一致。

**專案 partial class 結構：**
```
CommModule: COMM.C.cs + CommHelpers.cs + NetCore.cs
DbModule:   DB.C.cs + DB.C.Extra.cs + DB.C.GM.cs
```

**典型案例：CharFromRoom**

檔案 A（CommModule / COMM.C.cs）：
```csharp
public partial class CommModule
{
    public void CharFromRoom(CharData ch)
    {
        ch.InRoom.People.Remove(ch);
        ch.InRoom = null;
    }
}
```

檔案 B（HandlerModule / HANDLER.C.cs）：
```csharp
public partial class HandlerModule
{
    public void CharFromRoom(CharData ch)
    {
        // 更完整的版本，包含光源處理
        if (ch.IsAffected(AFF_GLOW))
            ch.InRoom.Light--;
        ch.InRoom.People.Remove(ch);
        ch.InRoom = null;
    }
}
```

**問題：**
- 若在不同類別 → 呼叫時不知該用哪個版本
- 若在同一 partial class → 編譯錯誤（重複定義）
- 修 Bug 時只修一個版本，另一個仍有問題

**高風險函式（跨檔案常見）：**
- `CharFromRoom` / `CharToRoom`
- `ObjFromChar` / `ObjToChar`
- `SendToChar` / `Act`
- 各種 Utility 函式

## 行動

1. 新增函式前，先 grep 整個 src-cs 目錄確認是否已存在
2. 若已存在，決定應該放在哪個類別
3. 移除重複的版本，保留最完整的
4. 更新所有呼叫點

```bash
grep -rn "void CharFromRoom" {CSHARP_DIR}/MudGM/Src/
```

## 驗證

- grep 每個函式名稱，確認只出現一次定義
- `dotnet build` 無重複定義錯誤
- 確認保留的版本是最完整的

## 失敗時

→ patterns/partial-class, verification/grep-existing
