# CStr 命名規則

> 來源: CStr.cs 現有慣例，cstr_add_missing.py
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md
> 相關原子: atoms/cstr/region-structure.md, atoms/cstr/new-file-setup.md
> 觸發條件: 新增 CStr 常數時；決定常數名稱

## 知識
CStr 常數命名遵循嚴格規則，確保一致性。

### 命名格式

#### 檔案特定字串
```
PREFIX_NNN
```
- `PREFIX`：來源檔案的代號（大寫）
- `NNN`：三位數流水號，從 001 開始

| C 原始檔     | PREFIX  | 範例          |
|-------------|---------|---------------|
| COMM.C      | COMM    | COMM_001      |
| DB.C        | DB      | DB_042        |
| ACT_WIZ.C   | AWIZ    | AWIZ_001      |
| ACT_COMM.C  | ACOMM   | ACOMM_015     |
| ACT_INFO.C  | AINFO   | AINFO_003     |
| ACT_MOVE.C  | AMOV    | AMOV_007      |
| ACT_OBJ.C   | AOBJ    | AOBJ_022      |
| FIGHT.C     | FIGHT   | FIGHT_088     |
| HANDLER.C   | HAND    | HAND_011      |
| MAGIC.C     | MAG     | MAG_005       |
| UPDATE.C    | UPD     | UPD_019       |

#### 共用/通用字串
```
M_USE_NNN
```
- 跨多個檔案使用的相同字串
- 放在 `#region Common Strings` 區塊

#### 陣列常數
```
PREFIX_ArrayName
```
- 用於整組字串陣列（如方向名、職業名）
- 例：`CONST_DirName`、`CONST_ClassName`

### 流水號規則
- 從 001 開始，依出現順序遞增
- 中間不跳號（除非刪除）
- 新增一律加在該 region 最後

### 範例
```csharp
public const string COMM_001 = "歡迎來到天乙神乩！";
public const string COMM_002 = "請輸入你的名字：";
public const string M_USE_001 = "你不能這麼做。\n";
```

## 行動
- 新增常數前確認 PREFIX 對應
- 查看該 region 最後一個編號，+1
- 共用字串放 M_USE region

## 驗證
- 命名符合 `PREFIX_NNN` 格式
- 編號不重複
- 執行 `cstr_add_missing.py` 無新增項目

## 失敗時
→ atoms/cstr/region-structure.md（確認 region 位置）
