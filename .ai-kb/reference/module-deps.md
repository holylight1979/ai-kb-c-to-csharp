# 模組依賴圖 (Module Dependencies)

> **模板提示**: 此檔案為範例。請根據你的專案模組結構修改依賴圖。

> 各模組之間的依賴關係，用於理解移植順序與編譯相依性

## 依賴圖

```
MercConstants ─────────────────────────────┐
MercTypes ─────────────────────────────────┤
CStr ──────────────────────────────────────┤ (被所有模組使用)
                                           │
DbModule ──────────────────────────────────┤
  ├── 讀取區域檔案、物件、怪物             │
  ├── 管理全域鏈結串列                     │
  └── 依賴: MercTypes, MercConstants       │
                                           │
HandlerModule ─────────────────────────────┤
  ├── 物件/角色/房間操作函數               │
  ├── affect_to_char, char_from_room 等    │
  └── 依賴: DbModule, MercTypes            │
                                           │
CommModule ────────────────────────────────┤
  ├── 網路通訊、主迴圈                     │
  ├── act(), send_to_char() 等             │
  └── 依賴: HandlerModule, DbModule        │
                                           │
InterpModule ──────────────────────────────┤
  ├── 指令解析與派發                       │
  └── 依賴: CommModule, HandlerModule      │
                                           │
SaveModule ────────────────────────────────┤
  ├── 角色存檔/讀檔                        │
  └── 依賴: DbModule, HandlerModule        │
                                           │
UpdateModule ──────────────────────────────┤
  ├── 遊戲世界更新（tick、weather 等）     │
  └── 依賴: HandlerModule, CommModule      │
                                           │
FightModule ───────────────────────────────┤
  ├── 戰鬥系統                             │
  └── 依賴: HandlerModule, CommModule      │
                                           │
ConstModule ───────────────────────────────┤
  ├── 靜態資料表（技能表、職業表等）       │
  └── 依賴: MercTypes, MercConstants       │
                                           │
ActCommModule ─── ActInfoModule ─── ActMoveModule ─── ActObjModule
  └── 玩家指令實作（各 ACT_*.C）
  └── 依賴: HandlerModule, CommModule, InterpModule
                                           │
ActWizModule ──────────────────────────────┤
  ├── 巫師指令                             │
  └── 依賴: 幾乎所有模組                   │
                                           │
SpecialModule ─────────────────────────────┤
  ├── 特殊函數（NPC 行為）                 │
  └── 依賴: HandlerModule, FightModule     │
                                           │
HuntModule ────────────────────────────────┘
  ├── 追蹤/獵殺系統
  └── 依賴: HandlerModule, ActMoveModule
```

## 關鍵依賴路徑

```
CommModule → HandlerModule → DbModule → MercTypes/MercConstants
```

這是最核心的依賴鏈。移植順序建議:
1. MercConstants + MercTypes（基礎型別與常數）
2. DbModule（資料載入）
3. HandlerModule（核心操作）
4. CommModule（通訊層）
5. 其餘模組（順序較彈性）

## 共用依賴

以下被所有模組使用:
- `MercConstants.cs` — 常數定義（MAX_LEVEL、PULSE_TICK 等）
- `MercTypes.cs` — 型別定義（CharData、ObjData、RoomData 等）
- `MercStubs.cs` — 共用輔助方法
- `CStr.cs` — 中文字串常數
- `DbStubs.cs` — 資料庫相關 stub

## 注意事項

- 循環依賴: C 原始碼中函數互相呼叫是常態，C# 用 partial class 處理
- ActWizModule 依賴最廣，幾乎需要所有其他模組才能完整移植
- SpecialModule 的 spec_fun 使用字串派發，避免直接函數指標依賴
