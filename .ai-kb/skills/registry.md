# Skill 登錄表 (Registry)

> 所有已註冊 Skill 的清單，含位置、用途及工作流程整合點

## 現有 Skill 清單

| 名稱 | 位置 | 用途 | 工作流程整合點 |
|------|------|------|----------------|
| `port_verifier` | _(專案特定路徑)_ | 自動化驗證移植正確性（編碼、常數、字串、stub） | VERIFY 階段全部使用 |
| `c_to_csharp_porting_toolkit` | _(專案特定路徑)_ | 自動化 C→C# 轉譯（regex 轉換、命名慣例、巨集展開） | SKELETON + PORT_FUNCTIONS |
| `c_porting_helper` | _(專案特定路徑)_ | C→C# 移植指南與常見替換模式 | PORT_FUNCTIONS 參考 |
| `encoding_checker` | _(專案特定路徑)_ | 偵測檔案編碼（Big5/CP950 vs UTF-8） | INIT + DETECT 階段 |
| `mud_area_tools` | _(專案特定路徑)_ | 分析與修改 MUD .ARE 檔案（房間搜尋、注入） | 非移植流程，區域編輯專用 |
| `room_art_creator` | _(專案特定路徑)_ | AI 輔助產生 MUD 房間 ASCII 美術 | 非移植流程，區域美化專用 |

## 自動建立的 Skill 空間

| 名稱 | 位置 | 用途 | 建立時機 |
|------|------|------|----------|
| _(預留)_ | `.claude/skills/{name}/` | 移植過程中發現的新模式 | PORT_FUNCTIONS 階段發現重複模式時 |
| _(預留)_ | `.claude/skills/{name}/` | 驗證過程中的專用修復 | ERROR_RECOVERY 階段需要自動化時 |

## Skill 與工作流程對應

```
port-new-file:
  INIT         → encoding_checker
  SKELETON     → c_to_csharp_porting_toolkit
  PORT_FUNCTIONS → c_porting_helper, c_to_csharp_porting_toolkit
  CSTR         → (Python 工具，非 skill)
  VERIFY       → port_verifier

verify-existing:
  SCAN         → port_verifier (encoding-scan, stub-scan)
  COMPARE      → port_verifier (compare-strings, compare-constants)

fix-corruption:
  DETECT       → encoding_checker, port_verifier (encoding-scan)
  DECODE       → (Python 工具 big5_extract.py)
```

## 備註

- Skill 的實際位置為專案特定路徑（如 `.agent/skills/` 或 `.claude/skills/`），依使用的 agent 而異
- 部署時需根據專案結構調整路徑
- 新 Skill 建立請參考 `creation-guide.md`
