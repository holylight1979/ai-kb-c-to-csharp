# Big5 編碼基礎

> 來源: 原始 C 原始碼檔案
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/encoding/cp950-vs-big5.md, atoms/encoding/0x5C-backslash.md, atoms/encoding/0x7E-tilde.md
> 觸發條件: 處理原始 C 原始碼或區域檔案中的中文文字

## 知識
Big5 是台灣/香港常用的繁體中文雙位元組編碼。

### 編碼結構
- ASCII 字元（0x00-0x7F）：單位元組，與 ASCII 完全相容
- 中文字元：雙位元組
  - 前導位元組（lead byte）：0x81-0xFE
  - 後隨位元組（trail byte）：0x40-0x7E 或 0xA1-0xFE
- 每個中文字 = 2 bytes

### 位元組範圍圖
```
前導位元組: 81 82 83 ... A1 A2 ... FE
後隨位元組: 40-7E, A1-FE
            ^^^^
            注意：包含 0x5C(\) 和 0x7E(~)
```

### 本專案狀況
- `SRC/` 目錄下的 `.C` 和 `.H` 檔案 → Big5 編碼
- `.ARE` 區域檔案 → Big5 編碼
- `src-cs/` 的 `.cs` 檔案 → UTF-8 編碼（已轉換）
- 網路 I/O（telnet）→ Big5 編碼（玩家端期望）

### 常見中文字範圍
- 常用字（A440-C67E）：一、丁、七... 到 鶴
- 次常用字（C940-F9D5）：較少見的字
- 符號區（A140-A3BF）：標點、符號

## 行動
- 讀取原始 C 原始碼時，必須以 Big5/cp950 模式開啟
- 絕對不要用 UTF-8 讀取 Big5 檔案（會產生亂碼）
- .cs 檔案中的中文已是 UTF-8，直接讀取即可

## 驗證
- 用十六進位檢視器確認 Big5 檔案的位元組結構
- Python: `open(f, 'rb').read().decode('cp950')` 無錯誤

## 失敗時
→ atoms/encoding/cp950-vs-big5.md（使用 cp950 而非 big5）
