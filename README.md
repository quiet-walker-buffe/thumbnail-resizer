# Thumbnail Resizer for Blog

ブログ用サムネイル画像を、
**画像編集ソフトを使わずに短時間で量産**できる Web アプリです。

Streamlit を使ってブラウザ上で動作します。

---

## 機能

- 画像アップロード（PNG / JPG / JPEG）
- サイズ指定でリサイズ（ブログやSNSの推奨サイズに即対応）
- 縦横比維持（画像が歪まない）
- テキスト追加（中央 / 上 / 下）
- 形式変換（PNG / JPEG）
- ZIP ダウンロード対応

---

## 想定ユーザー

- ブログ記事を書くたびにサムネ作成が面倒な人
- 画像編集ソフトを起動したくない人
- 同じサイズの画像を何枚も作る必要がある人

---

## 使い方

1. 画像をアップロード
2. 幅・高さを指定
3. 必要なら文字を入力
4. ダウンロードボタンを押す

---

## 公開 URL

(https://quiet-walker-buffe-thumbnail-resizer-app-5yrzzm.streamlit.app/)

---

## ローカル実行方法

```bash
pip install -r requirements.txt
streamlit run app.py
```
---

## 📸 UIイメージ

### 1. 画像アップロード画面
![画像アップロード画面](images/resizer_top.png)

### 2. サイズ設定・プレビュー画面
![サイズ設定とプレビュー](images/resizer_settings.png)
