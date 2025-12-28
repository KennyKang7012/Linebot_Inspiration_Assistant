# 疑難排解 (Troubleshooting)

本文件紀錄開發過程中遇到的常見問題及其解決方案。

## Git 推送失敗：RPC failed; HTTP 400

### 問題描述
執行 `git push` 時出現以下錯誤：
```text
error: RPC failed; HTTP 400 curl 22 The requested URL returned error: 400
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
```

### 原因分析
這通常發生在透過 HTTPS 推送較大檔案或較多變更時，Git 的 HTTP 快取區 (Buffer) 不足或連線超時。

### 解決方案

#### 方法一：增加 Git HTTP 快取 (推薦)
在終端機執行以下指令，將過大的快取區增加到 500MB：
```bash
git config --global http.postBuffer 524288000
```

#### 方法二：檢查並移除大檔案
如果是因為不小心將高解析度圖片或二進位檔 commit 進去，請先移除該檔案並清理 Git 歷史：
1.  **物理刪除檔案**。
2.  **更新 `.gitignore`** 防止未來再次被加入。
3.  **重置 Commit 記錄** (若已 commit)：
    ```bash
    git reset --soft [前一個安全的commit_id]
    git rm --cached [大檔案路徑]
    git commit -m "修正：移除大檔案並重整記錄"
    ```
4.  **強制推送**：
    ```bash
    git push -f origin main
    ```

---
*最後更新：2025-12-29*
