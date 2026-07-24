# 灰域 / Gray Domain

小說發佈站。純靜態網站（HTML/CSS/JS，無框架、無外部相依），可直接部署到 Vercel、GitHub Pages 等。

## 結構

```
index.html          目錄首頁（自動生成）
chapters/
  epNN.md           每一話的原始 Markdown（手寫）
  epNN.html         對應的閱讀頁（自動生成）
assets/
  style.css         電子書排版樣式（支援明暗模式）
  reader.js         明暗切換 + 字級記憶
build.py            建置腳本（零依賴，Python 3）
```

## 發佈新的一話

1. 把新一話存成 `chapters/epNN.md`（依序命名：`ep02.md`、`ep03.md`……，檔名決定順序）。
2. 執行建置：

   ```bash
   python3 build.py
   ```

3. 提交並推上 GitHub，Vercel 會自動重新部署。

## Markdown 寫法慣例

| 寫法 | 效果 |
|------|------|
| `# 第二話` | 章節標題（會自動去掉《灰域》書名號與「・」後綴） |
| 空行分段 | 段落 |
| `**文字**` | 粗體（心聲／內心獨白） |
| `---` | 場景分隔線 |
| `*   *   *` | 較大的段落／視角切換（星號裝飾） |
| `「……」` | 對話 |

> 標題行只要寫 `# 第二話` 即可；若沿用 `# 《灰域》第二話・散文稿` 也能正確處理。

## 部署（Vercel）

這是純靜態站，Vercel 無需任何建置設定：Framework Preset 選「Other」，Build Command 留空，Output Directory 留空（根目錄即網站根）。連上此 repo 後每次 push 會自動部署。
