# CStr.cs Region 結構

> 來源: CStr.cs 檔案結構
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md
> 相關原子: atoms/cstr/naming-rules.md, atoms/cstr/new-file-setup.md
> 觸發條件: 新增常數到 CStr.cs；尋找特定常數的位置

## 知識
CStr.cs 使用 `#region` / `#endregion` 組織常數，每個 region 對應一個來源檔案。

### 結構概覽
```csharp
public static class CStr
{
    #region Common Strings
    // M_USE_001 ... M_USE_NNN
    // 跨檔案共用的字串
    #endregion

    #region COMM
    // COMM_001 ... COMM_NNN
    #endregion

    #region DB
    // DB_001 ... DB_NNN
    #endregion

    #region ACT_WIZ
    // AWIZ_001 ... AWIZ_NNN
    #endregion

    #region ACT_COMM
    // ACOMM_001 ...
    #endregion

    #region ACT_INFO
    // AINFO_001 ...
    #endregion

    #region ACT_MOVE
    // AMOV_001 ...
    #endregion

    #region ACT_OBJ
    // AOBJ_001 ...
    #endregion

    #region FIGHT
    // FIGHT_001 ...
    #endregion

    #region HANDLER
    // HAND_001 ...
    #endregion

    #region MAGIC
    // MAG_001 ...
    #endregion

    #region UPDATE
    // UPD_001 ...
    #endregion

    #region CONST
    // CONST_001 ... 及陣列常數
    #endregion
}
```

### 排序規則
- 每個 region 內部：按流水號遞增排序
- Region 之間：Common 在最前，其餘按字母順序
- 新增常數一律加在該 region 的最末尾

### 新增 region（移植新檔案時）
```csharp
    #region NEWFILE
    // 在此新增 NEWPREFIX_001 等常數
    #endregion
```
插入位置：按字母順序排在正確位置。

## 行動
- 新增常數時，找到對應 region 的 `#endregion` 前一行
- 新增 region 時，按字母順序插入
- 確保 `#region` 和 `#endregion` 配對正確

## 驗證
- `dotnet build` 編譯通過
- 每個 region 內部編號遞增無跳號
- 無重複常數名稱

## 失敗時
→ atoms/cstr/naming-rules.md（確認命名規則）
