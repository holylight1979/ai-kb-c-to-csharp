# Skill 建立指南 (Creation Guide)

> 如何建立新的 Skill，包含前置元資料格式、標準模板、觸發條件

## Skill 檔案位置

```
.claude/skills/{skill-name}/SKILL.md
```

命名慣例: 使用 `snake_case`，如 `fix_big5_tilde`、`port_magic_system`

## SKILL.md 前置元資料格式 (Frontmatter)

```yaml
---
name: skill_name
description: 用一句話描述此 Skill 的功能（繁體中文）
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---
```

### 欄位說明

| 欄位 | 必要 | 說明 |
|------|------|------|
| `name` | 是 | Skill 唯一識別名，與目錄名一致 |
| `description` | 是 | 簡短描述，用於 registry 和搜尋 |
| `user-invocable` | 是 | 是否可由使用者直接呼叫（通常為 `false`） |
| `allowed-tools` | 否 | 此 Skill 可使用的工具清單 |

## 標準模板結構

```markdown
---
name: my_new_skill
description: 描述此 Skill 的功能
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Edit
---

# Skill 名稱

說明此 Skill 的用途與背景。

## 觸發條件

描述何時應自動觸發此 Skill。

## 執行步驟

1. 第一步
2. 第二步
3. 第三步

## 成功標準

- 標準 1
- 標準 2

## 自我修正記錄

| 日期 | 問題 | 修正 |
|------|------|------|
| _(首次建立)_ | _(無)_ | _(無)_ |
```

## 自動建立的觸發條件

在以下情況下，應考慮建立新 Skill:

1. **重複模式**: 同一類型的修復或轉換在 3 個以上檔案中重複出現
2. **複雜子流程**: 某個步驟超過 10 個動作且可被封裝
3. **錯誤修復模式**: ERROR_RECOVERY 中同一類錯誤出現 2 次以上
4. **新檔案類型**: 移植到新的 C 檔案類別（如 MAGIC 系列）

## 建立流程

1. 確認觸發條件已滿足
2. 在 `.claude/skills/` 下建立目錄
3. 使用標準模板建立 `SKILL.md`
4. 在 `registry.md` 中新增登錄
5. 若有輔助腳本，放在同一目錄下

## 自我修正記錄區段

每個 Skill 應包含自我修正記錄，用於追蹤:
- 執行過程中發現的問題
- 對 Skill 邏輯的調整
- 失敗案例與改進措施

格式為表格，新記錄追加到底部。這有助於 Skill 隨時間演進。

## 已有模板

- `templates/verify-skill-template.md` — 驗證型 Skill
- `templates/port-skill-template.md` — 移植型 Skill
