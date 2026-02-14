# 驗證型 Skill 模板

> 複製此模板並填入具體內容，用於建立新的驗證型 Skill

```markdown
---
name: verify_{target_name}
description: 驗證 {目標} 的正確性
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# {目標} 驗證器

驗證 {目標檔案/模組} 的移植正確性。

## 觸發條件

- 當 {目標檔案} 完成移植後自動觸發
- 當 verify-existing 工作流程指定此檔案時觸發
- 當 ERROR_RECOVERY 階段需要重新驗證時觸發

## 執行步驟

1. 執行 encoding-scan，確認零 FFFD/PUA:
   ```bash
   python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src/{target}.cs
   ```

2. 執行 stub-scan，列出殘留 TODO/stub:
   ```bash
   python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src/{target}.cs
   ```

3. 執行 compare-strings，比對中文字串:
   ```bash
   python -X utf8 verify.py compare-strings SRC/{TARGET}.C {CSHARP_DIR}/MudGM/Src/{target}.cs
   ```

4. （若適用）執行 compare-constants:
   ```bash
   python -X utf8 verify.py -v compare-constants SRC/{HEADER}.H {CSHARP_DIR}/MudGM/Src/{target}.cs
   ```

5. 彙整結果，生成驗證報告

## 成功標準

- [ ] FFFD = 0, PUA = 0
- [ ] 無 CRITICAL stub（NotImplementedException 可接受於非核心路徑）
- [ ] 字串覆蓋率 >= 95%
- [ ] 常數數值全部正確（若適用）
- [ ] dotnet build 通過

## 自我修正記錄

| 日期 | 問題 | 修正 |
|------|------|------|
| _(首次建立)_ | _(無)_ | _(無)_ |
```
