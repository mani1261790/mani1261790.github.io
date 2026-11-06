# mani portfolio

静的HTMLのポートフォリオです。ローカル確認は `python3 -m http.server 8080` で起動します。

## 作品の更新

`projects.json` に作品名・説明・用途・リンクをまとめています。用途は `categories` に定義した共通分類から一つ選びます。技術名や公開状況は説明文に書き、用途タグと混在させません。

編集後は `python3 scripts/build-portfolio.py` を実行し、生成された `index.html` も一緒にコミットしてください。作品は静的HTMLとして出力されるため、JavaScriptが無効でも読めます。

Design-Qualityには公開リポジトリへのリンクを設けていません。ToolUseProxy-showcaseはToolUseProxyの検証デモとして掲載しています。フォークと、このポートフォリオ自体は作品の追加対象にしていません。

作品の `id` はモーダルを識別する固定値です。`details` に見出しと本文を追加すると詳しい紹介に反映されます。カード全体から開けて、閉じるボタン・Escape・背景クリックで一覧に戻ります。JavaScript無効時も概要と外部リンクは表示されます。

## GitHub活動カレンダー

`python3 scripts/update-contributions.py` でGitHubの公開プロフィールから直近1年のカレンダーを取得し、`index.html` の該当部分だけ更新します。閲覧時の外部サービス接続やトークンは不要です。取得形式が変わった場合は更新を失敗させ、前回の表示を残します。

`.github/workflows/update-contributions.yml` は毎日06:23 JSTに更新し、現在のmainブランチを配信するGitHub Pagesの再ビルドを要求します。mainへの公開後に動作します。Actionsでの書き込み・Pagesビルド権限が必要です。取得日は画面にも表示します。

## 作品画像

`projects.json` の `images` に `src`・`alt`・`caption`・`width`・`height` を指定すると、紹介モーダルの冒頭に画像が表示されます。画像は `assets/projects/` に置きます。原寸画像は別タブで開き、紹介モーダルの位置を保持します。

2026-11-07追加分：PhotoTexteの比較画面とNoemaのスマホ画面を掲載。Noemaトップ・25分タイマー・ToolUseProxyの公開デモログは公開サイトを撮影。Vidarrは公開リポジトリの `docs/branding/vidarr-logo-1024.png`、ノート用紙は既存の配布PDFの1ページ目を使用しています。画像に合わせて架空のUIは作成していません。
