# Compare Constants Verification

> 來源: MERC.H 審計, 常數完整性檢查
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: build-check, using-static-import
> 觸發條件: 移植常數定義後、審計 MercConstants.cs 時

## 知識
比較 C 的 `#define` 常數值與 C# 的 `const` 值。
MERC.H 審計發現的嚴重問題：

已知錯誤值（已修正或待修正）：
```
PULSE_TICK:           C = 92,  C# 曾為 60  → 錯誤！
VECT_SECT_CANT_LOGIN: C = 0x0020, C# 曾為 0x0010 → 錯誤！
VECT_SECT_CANT_QUIT:  C = 0x0040, C# 曾為 0x0020 → 錯誤！
```

掃描結果分類：
- **MATCH**: 值一致 → 正確
- **MISMATCH**: 值不同 → 必須修正
- **MISSING**: C 有但 C# 沒有 → 評估是否需要

加 `-v` 旗標可顯示所有比對細節（包含 MATCH）。
預設只顯示 MISMATCH 和 MISSING。

MERC.H 審計統計：
- 約 422 個常數中，約 247 個缺失
- 3 個值錯誤
- 部分缺失常數可能在其他檔案中定義

## 行動
```bash
cd {CSHARP_DIR}
python -X utf8 verify.py -v compare-constants SRC/MERC.H {CSHARP_DIR}/MudGM/Src/MercConstants.cs
```

快速檢查（只看問題）：
```bash
python -X utf8 verify.py compare-constants SRC/MERC.H {CSHARP_DIR}/MudGM/Src/MercConstants.cs
```

## 驗證
MISMATCH 數量應為 0。
MISSING 項目應有記錄說明為何不需要，或加入待辦清單。

## 失敗時
→ decode-big5 (確認 C 原始碼中的正確值)
→ build-check (修正後編譯驗證)
