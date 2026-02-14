# 檔案前綴映射表 (File-Prefix Map)

> **模板提示**: 此檔案為範例。請根據你的專案修改下方映射表。

> C 原始檔 → C# 檔案 → CStr 前綴 → Module 類別的完整對應

## 映射表

| # | C 原始檔 | C# 檔案 | CStr 前綴 | Module 類別 |
|---|----------|---------|-----------|-------------|
| 1 | DB.C | DB.C.cs | DB | DbModule |
| 2 | DB.C | DB.C.Extra.cs | DB | DbModule |
| 3 | DB.C | DB.C.GM.cs | DB | DbModule |
| 4 | COMM.C | COMM.C.cs | COMM | CommModule |
| 5 | COMM.C | CommHelpers.cs | COMM | CommModule |
| 6 | COMM.C | NetCore.cs | COMM | CommModule |
| 7 | HANDLER.C | HANDLER.C.cs | HANDLER | HandlerModule |
| 8 | INTERP.C | INTERP.C.cs | INTERP | InterpModule |
| 9 | UPDATE.C | UPDATE.C.cs | UPDATE | UpdateModule |
| 10 | SAVE.C | SAVE.C.cs | SAVE | SaveModule |
| 11 | SAVE.C | SAVE.C.Reader.cs | SAVE | SaveModule |
| 12 | ACT_COMM.C | ACT_COMM.C.cs | ACTCOMM | ActCommModule |
| 13 | ACT_INFO.C | ACT_INFO.C.cs | ACTINFO | ActInfoModule |
| 14 | ACT_MOVE.C | ACT_MOVE.C.cs | ACTMOVE | ActMoveModule |
| 15 | ACT_OBJ.C | ACT_OBJ.C.cs | ACTOBJ | ActObjModule |
| 16 | ACT_WIZ.C | ACT_WIZ.C.Port.cs | ACTWIZ | ActWizModule |
| 17 | FIGHT.C | FIGHT.C.cs | FIGHT | FightModule |
| 18 | CONST.C | CONST.C.cs | CONST | ConstModule |
| 19 | MERC.H | MercStubs.cs | M_USE | (共用常數) |
| 20 | SPECIAL.C | SPECIAL.C.cs | SPECIAL | SpecialModule |
| 21 | SPECIAL.C | SPECIAL.C.Part2.cs | SPECIAL | SpecialModule |
| 22 | SPECIAL.C | SPECIAL.C.Part3.cs | SPECIAL | SpecialModule |
| 23 | HUNT.C | HUNT.C.cs | HUNT | HuntModule |

## CStr.cs Region 對應

| CStr 前綴 | #region 名稱 |
|-----------|--------------|
| M_USE | Common Strings |
| CONST | CONST |
| COMM | COMM |
| DB | DB |
| HANDLER | HANDLER |
| INTERP | INTERP |
| UPDATE | UPDATE |
| SAVE | SAVE |
| ACTCOMM | ACTCOMM |
| ACTINFO | ACTINFO |
| ACTMOVE | ACTMOVE |
| ACTOBJ | ACT_OBJ.C |
| ACTWIZ | ACTWIZ |
| FIGHT | FIGHT |
| SPECIAL | SPECIAL |
| HUNT | HUNT |

## 備註

- 一個 C 原始檔可能對應多個 C# 檔案（partial class 拆分）
- 同一前綴的多個 C# 檔案共用同一個 CStr region
- `MercStubs.cs` 使用 `M_USE` 前綴，對應 "Common Strings" region
- ACTOBJ 前綴的 region 名稱是 `ACT_OBJ.C`（歷史原因，名稱不一致）
