# AI Knowledge Base for C→C# Porting (Big5/MUD)

AI 自主執行 C→C# MUD 伺服器移植的知識引擎模板。

## 這是什麼？

一套 **83 個 Markdown 文件 + 3 個 Python 工具**，讓 AI（Claude Code）能夠：

- 收到「移植 XXX.C」指令後，**零人工介入**完成整個 C→C# 移植
- 自動分類函數風險等級，批次驗證低風險函數
- 自動偵測 20 種已知陷阱（編碼損壞、邏輯遺漏、格式錯誤...）
- 自動集中化中文字串（Big5→UTF-8→CStr 常數）
- 自動建立、測試、進化 Skill

## 快速開始

### 1. 複製到你的專案

```bash
git clone https://github.com/holylight1979/ai-kb-c-to-csharp.git
cp -r ai-kb-c-to-csharp/.ai-kb  你的專案/
cp -r ai-kb-c-to-csharp/tools/  你的專案/.claude/tools/
```

### 2. 自訂 3 個變數

在以下檔案中搜尋並替換 `{佔位符}` 為你的實際路徑：

| 佔位符 | 說明 | 範例 |
|--------|------|------|
| `{PROJECT_ROOT}` | 專案根目錄 | `F:\MyProject` |
| `{CSHARP_DIR}` | C# 專案目錄（相對於專案根） | `MyCSharpProject` |
| `{CSPROJ_PATH}` | .csproj 檔案路徑（相對路徑） | `MyCSharpProject/MyApp.csproj` |

```bash
# 批次替換（在 .ai-kb/ 目錄下執行）
grep -rl "{CSHARP_DIR}" .ai-kb/ | xargs sed -i 's|{CSHARP_DIR}|MyCSharpProject|g'
grep -rl "{PROJECT_ROOT}" .ai-kb/ | xargs sed -i 's|{PROJECT_ROOT}|F:\\MyProject|g'
grep -rl "{CSPROJ_PATH}" .ai-kb/ | xargs sed -i 's|{CSPROJ_PATH}|MyCSharpProject/MyApp.csproj|g'
```

### 3. 自訂 2 個檔案

| 檔案 | 動作 |
|------|------|
| `.ai-kb/reference/file-prefix-map.md` | 填入你的 C 原始檔 → C# 檔案 → CStr 前綴映射 |
| `.ai-kb/reference/module-deps.md` | 填入你的模組依賴圖 |

### 4. 自訂 Python 工具

編輯 `.claude/tools/` 下的 3 個 Python 檔案，修改標有 `TODO` 的行：

```python
# cstr_add_missing.py 和 cstr_replacer.py 中：
CSHARP_ROOT = PROJECT_ROOT / 'YourCSharpProject'  # ← 改為你的 C# 目錄
FILE_TO_PREFIX = {
    'YOUR_FILE.C.cs': 'YOUR_PREFIX',  # ← 改為你的映射
}

# big5_extract.py 中：
SRC_DIR = PROJECT_ROOT / 'SRC'  # ← 改為你的 C 原始碼目錄
```

### 5. 加入 CLAUDE.md 自動化指令

將 `CLAUDE.md.template` 的內容複製到你專案的 `CLAUDE.md` 中。

**這一步最重要** — 沒有這段指令，AI 不會自動使用知識庫。

### 6. 開始使用

```
你: 移植 ACT_OBJ.C
AI: (自動讀取 INDEX.md → workflow → 分類 → 移植 → 驗證 → 完成)
```

## 檔案結構

```
.ai-kb/
├── INDEX.md                    # AI 入口（所有任務從這裡開始）
├── algorithms/          (8)    # 決策引擎（風險分類、陷阱偵測、記憶管理...）
├── atoms/
│   ├── encoding/        (7)    # Big5/CP950 編碼知識
│   ├── cstr/            (7)    # CStr 字串集中化規則
│   ├── syntax/         (11)    # C→C# 語法轉換規則
│   ├── patterns/        (8)    # 架構模式（partial class、stub、delegation...）
│   ├── traps/          (20)    # 20 種已知陷阱（1:1 對應驗證指南）
│   └── verification/    (8)    # 驗證步驟（build、encoding、strings...）
├── tools/               (3)    # Python 工具操作手冊
├── workflows/           (3)    # 狀態機流程（移植、驗證、修復亂碼）
├── skills/              (4)    # Skill 自我成長閉環藍圖
├── reference/           (3)    # 速查表（需自訂）
└── workspace/                  # 工作暫存區（不入 git）

tools/                          # Python 工具（複製到 .claude/tools/）
├── big5_extract.py             # Big5 字串提取
├── cstr_add_missing.py         # 新增缺少的 CStr 常數
├── cstr_replacer.py            # 替換硬編碼字串為 CStr 引用
└── README.md                   # 工具使用說明
```

## 核心系統

### 1. 反幻覺守衛
- 風險分類器：LOW/MEDIUM/HIGH/CRITICAL
- LOW 函數批次 5-10 個一起 build（省時）
- CRITICAL 函數逐行比對 + 全套驗證（求正確）

### 2. 記憶生命週期
- 長期記憶（atoms/）、會話暫存（session/）、待精煉（staging/）、報告（reports/）
- 任務完成後自動 REFINE：有價值的發現升級為原子，其餘清除

### 3. Skill 自我成長閉環
- DETECT（偵測重複操作）→ CREATE → TEST → CORRECT → DEPLOY → MONITOR → EVOLVE
- 全程零人工介入

## 適用場景

- Big5 編碼的 C MUD 伺服器移植到 C#
- Merc/ROM/Envy 系列 MUD 原始碼
- 任何需要 Big5→UTF-8 + CStr 集中化的 C→C# 專案

## 授權

MIT License
