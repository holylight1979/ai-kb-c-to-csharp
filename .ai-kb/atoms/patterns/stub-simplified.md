# Simplified Stub Pattern

> 來源: audit-findings.md, DB.C / COMM.C 審計結果
> 信心度: VERIFIED
> 前置知識: stub-empty
> 相關原子: stub-empty, function-call-vs-assign, line-count-check
> 觸發條件: 審計「看似完成」的 C# 函式時

## 知識
簡化 stub 比空殼 stub 更危險，因為它「看起來完成了」但邏輯只做了一半。

典型案例：`extract_char` 在 C 中有 8 個清理步驟：
1. 從房間移除角色
2. 清除所有戰鬥引用（遍歷 char_list）
3. 移除所有 affect
4. 移除身上裝備
5. 移除背包物品
6. 從 char_list 移除
7. 從 master/follower 鏈結移除
8. 釋放記憶體

但 C# 版本可能只實作了 1、3、4 步，省略了關鍵的全域清理。

偵測方法：
```
C 版本行數: 45 行
C# 版本行數: 12 行
比率: 3.75x → 高度可疑
```

相關陷阱：G-cleanup-truncated（清理步驟被截斷）、
H-logic-omitted（邏輯被省略）。

## 行動
1. 使用 `decode-big5` 逐行閱讀 C 原始碼
2. 列出所有邏輯步驟並編號
3. 逐一對照 C# 實作，標記缺失項
4. 補齊所有缺失的邏輯步驟

## 驗證
使用 line-count-check 比較行數比率。
若 C 行數 > C# 行數 × 3，需逐行審查。

## 失敗時
→ line-count-check (量化差距)
→ decode-big5 (重新閱讀原始碼)
→ compare-strings (確認字串完整性)
