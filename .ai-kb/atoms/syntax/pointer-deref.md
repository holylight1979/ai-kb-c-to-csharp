# 指標解參考轉換

> 來源: 全專案通用，MERC.H 結構定義
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/global-linked-list.md
> 觸發條件: 看到 C 的 `->` 運算子或 `*ptr` 解參考

## 知識
C 使用 `->` 存取指標成員，C# 全部改用 `.` 點號，並套用 PascalCase：

```c
ch->level           →  ch.Level
ch->pcdata->pwd     →  ch.PcData.Password
obj->in_room->vnum  →  obj.InRoom.Vnum
ch->hit             →  ch.Hit
ch->max_hit         →  ch.MaxHit
```

命名轉換規則：
| C 命名風格      | C# 命名風格     | 範例                    |
|-----------------|-----------------|-------------------------|
| `snake_case`    | `PascalCase`    | `max_hit` → `MaxHit`   |
| `pcdata`        | `PcData`        | 縮寫保留語意            |
| `short_descr`   | `ShortDescr`    | 保留原始縮寫            |
| `in_room`       | `InRoom`        | 介詞合併                |

指標比較轉換：
```c
if (ch->fighting != NULL)   →  if (ch.Fighting != null)
if (ch->in_room == NULL)    →  if (ch.InRoom == null)
```

雙重指標（指標的指標）通常變成 ref 參數或直接回傳：
```c
void func(CHAR_DATA **ch)  →  void Func(ref CharData ch)
```

## 行動
- `->` 全部替換為 `.`
- 欄位名稱全部 PascalCase
- `NULL` 替換為 `null`
- 雙重指標視情況用 `ref` 或回傳值

## 驗證
- 編譯通過，欄位名稱與 CharData/ObjData 等類別定義一致
- 無 CS0103（名稱不存在）錯誤

## 失敗時
→ 檢查 MercTypes.cs 確認欄位的 C# 名稱
