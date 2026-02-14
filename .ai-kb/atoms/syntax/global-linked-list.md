# 全域連結串列轉換

> 來源: DB.C, HANDLER.C, MERC.H
> 信心度: VERIFIED
> 前置知識: atoms/syntax/pointer-deref.md, atoms/syntax/malloc-free.md
> 相關原子: 無
> 觸發條件: 看到 C 的 `for(x=list; x; x=x->next)` 走訪模式

## 知識
MUD 原始碼大量使用全域連結串列，走訪模式固定：

### 基本走訪
```c
CHAR_DATA *ch;
for (ch = char_list; ch != NULL; ch = ch->next) {
    // process ch
}
```
```csharp
foreach (var ch in CharList) {
    // process ch
}
```

### 常見全域串列
| C 全域變數         | C# 對應              | 元素型別    |
|-------------------|----------------------|------------|
| `char_list`       | `CharList`           | CharData   |
| `obj_list`        | `ObjList`            | ObjData    |
| `descriptor_list` | `DescriptorList`     | DescData   |
| `room_list`       | 通常用 Dictionary    | RoomData   |

### 走訪中刪除（危險模式）
```c
for (ch = char_list; ch != NULL; ch = ch_next) {
    ch_next = ch->next;  // 先保存 next
    if (should_remove(ch)) extract_char(ch);
}
```
```csharp
// 方案一：反向走訪
for (int i = CharList.Count - 1; i >= 0; i--) {
    if (ShouldRemove(CharList[i])) ExtractChar(CharList[i]);
}
// 方案二：ToList() 複製
foreach (var ch in CharList.ToList()) {
    if (ShouldRemove(ch)) ExtractChar(ch);
}
```

### 搜尋模式
```c
for (ch = char_list; ch; ch = ch->next)
    if (ch->in_room == room && IS_NPC(ch))
        return ch;
```
```csharp
return CharList.FirstOrDefault(ch => ch.InRoom == room && IsNpc(ch));
```

## 行動
- 全域串列改用 `List<T>` 靜態欄位
- for+next 走訪 → foreach 或 LINQ
- 走訪中刪除 → 反向 for 或 ToList()

## 驗證
- 走訪順序與 C 版一致
- 走訪中刪除不拋出 InvalidOperationException

## 失敗時
→ atoms/syntax/malloc-free.md（記憶體管理模式）
