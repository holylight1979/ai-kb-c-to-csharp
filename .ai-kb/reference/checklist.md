# 移植驗證檢查清單 (Verification Checklist)

> 20 項檢查，作為標記檔案完成前的最終簽核。結合黃金守則、陷阱檢查、CStr 工作流程步驟。

## 使用方式

每完成一個 .cs 檔案的移植，逐項確認以下 20 點。
全部通過後才可在 TODO.md 中標記為已完成。

---

## A. 編碼與解碼（3 項）

- [ ] **A1** encoding-scan 結果: FFFD = 0, PUA = 0
- [ ] **A2** 原始 C 檔案使用 cp950（非 big5）正確解碼，無亂碼
- [ ] **A3** fread_string 實作中有 Big5 tilde（0x7E 作為第二位元組）保護

## B. 函數完整性（3 項）

- [ ] **B4** 所有 C 函數皆已移植（比對原始檔函數清單）
- [ ] **B5** stub-scan 無 CRITICAL stub（NotImplementedException 僅限非核心路徑）
- [ ] **B6** 無遺漏的 TODO/FIXME 標記（或已記錄在 TODO.md 中）

## C. 字串集中化（4 項）

- [ ] **C7** big5_extract --verify 顯示 100% 覆蓋（或已知排除項有記錄）
- [ ] **C8** cstr_add_missing --dry-run 顯示 0 new（所有常數已存在）
- [ ] **C9** cstr_replacer --analyze 顯示 MISSING = 0
- [ ] **C10** 原始檔中無殘留硬編碼中文字串（CStr. 引用除外）

## D. 陷阱檢查（5 項）

- [ ] **D11** 無殘留 `sprintf` / `printf`（應轉為 string.Format 或插值字串）
- [ ] **D12** switch 語句無隱式 fallthrough（C# 要求明確 break/return/goto）
- [ ] **D13** 無殘留 `str_cmp` / `str_prefix`（應轉為 .Equals / .StartsWith）
- [ ] **D14** 指標算術已轉為陣列索引或 ref 參數
- [ ] **D15** goto 語句已重構為迴圈/方法呼叫（或有正當理由保留）

## E. 型別與常數（3 項）

- [ ] **E16** compare-constants 結果: 所有數值正確（若適用）
- [ ] **E17** 型別映射正確: sh_int→short, char*→string, bool→bool
- [ ] **E18** 巨集已展開為方法或常數（IS_AWAKE, IS_NPC 等）

## F. 建置與整合（2 項）

- [ ] **F19** `dotnet build {CSPROJ_PATH}` 零錯誤、零警告（或已知警告已記錄）
- [ ] **F20** FILE_TO_PREFIX 映射已同步更新於 cstr_add_missing.py 和 cstr_replacer.py

---

## 簽核記錄

```
檔案: _______________
日期: _______________
通過項目: ___/20
未通過項目: _______________
備註: _______________
```

## 快速參考: 常見不通過原因

| 檢查項 | 常見原因 | 修復方式 |
|--------|----------|----------|
| A1 | 使用 big5 而非 cp950 | 重新以 cp950 解碼 |
| C9 | 未先執行 cstr_add_missing | 執行 cstr_add_missing 後重試 |
| D11 | 直接翻譯 sprintf 未轉型 | 改為 string.Format 或 $"" |
| D12 | C 語言 switch fallthrough 習慣 | 每個 case 加 break |
| F19 | 缺少 using 或型別未定義 | 檢查 MercTypes/MercStubs |
