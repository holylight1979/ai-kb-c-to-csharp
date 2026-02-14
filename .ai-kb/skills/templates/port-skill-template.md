# 移植型 Skill 模板

> 複製此模板並填入具體內容，用於建立新的移植型 Skill

```markdown
---
name: port_{target_name}
description: 移植 {C 檔案} 到 C#
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# {C 檔案} 移植器

將 {SRC/TARGET.C}（Big5）移植為 {CSHARP_DIR}/MudGM/Src/TARGET.C.cs（UTF-8 C#）。

## 觸發條件

- 當使用者要求移植 {TARGET.C} 時觸發
- 當 port-new-file 工作流程進入此檔案時觸發

## 執行步驟

1. 讀取 C 原始碼，確認 cp950 解碼:
   ```bash
   python -X utf8 .claude/tools/big5_extract.py SRC/{TARGET}.C --verify
   ```

2. 建立 C# 骨架檔案 `{TARGET}.C.cs`:
   - partial class 歸屬: {ModuleName}Module
   - 命名空間: MudGM
   - 列出所有函數並風險分級

3. 逐批移植函數（依風險等級）:
   - LOW: 批次 5-10 → build
   - MEDIUM: 批次 2-3 → build
   - HIGH/CRITICAL: 逐一 → build

4. 字串集中化:
   ```bash
   python -X utf8 .claude/tools/cstr_add_missing.py
   python -X utf8 .claude/tools/cstr_replacer.py --apply {TARGET}.C.cs
   dotnet build {CSPROJ_PATH}
   ```

5. 最終驗證:
   ```bash
   python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src/{TARGET}.C.cs
   python -X utf8 verify.py compare-strings SRC/{TARGET}.C {CSHARP_DIR}/MudGM/Src/{TARGET}.C.cs
   python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src/{TARGET}.C.cs
   ```

## 成功標準

- [ ] 所有函數已移植（無遺漏）
- [ ] dotnet build 零錯誤
- [ ] encoding-scan 零 FFFD/PUA
- [ ] CStr 覆蓋率 100%（MISSING = 0）
- [ ] stub-scan 無 CRITICAL stub
- [ ] TODO.md 已更新

## 自我修正記錄

| 日期 | 問題 | 修正 |
|------|------|------|
| _(首次建立)_ | _(無)_ | _(無)_ |
```
