# EIDOLie プレイ記録

対象: 第四境界 GUEST ARG「三人組アイドルEIDOLieは■■なのか」（作: いさかわ / yoryormary）
URL: https://yoryormary.com/eidoLie/index.html

## 方針
- ゲーム画面（ヘッドレスChromium）を **UIだけで** 操作する。ソースの解析はしない。
- 読み取る文字は、表示中のウィンドウに見えているものだけに限る（`tools/play.py` の `visible_frames`）。
- 詰まったときだけ公式ヒントページを使い、使ったことを記録する。

## データ
- `data/actions.jsonl`: 全操作のログ（時刻、コマンド、入力、結果、ブラウザタイトル＝進捗 `[n/43]`、スクリーンショット名）
- `data/screenshots/`: 操作ごとのスクリーンショット
- `python tools/summarize.py`: ページ発見の時系列、検索回数、ヒント使用回数を集計する

## 汚染（事前情報）の記録
- プレイ開始前の下調べで `docs/config.js` のページ定義（ファイル名の一覧）を見てしまった。
  そのため「在原業平」を検索語に選んだ判断は、ファイル名 `narihira_wiki` に影響された可能性がある。
- それ以外のページ本文や検索キーワードの定義は読んでいない。

## 環境上の制約
- ゲーム内のMV（YouTube埋め込み）は、この環境のネットワークポリシーで `www.youtube.com` が遮断されていて再生できない。
  ヒント5によると、進行にはMVの視聴が必要。
  - ネットワークでYouTubeを許可した後も、埋め込みプレイヤーは「Video unavailable」になった（User-Agentを通常のChromeにしても同じ）。
  - yt-dlpでは、動画の情報（「EIDOLie - Secret Voice [Official Music Video]」/ いさかわ）は取れたが、本体は「Sign in to confirm you're not a bot」で拒否された。
- ニュースサイト（JN News）の検索窓は入力できない（飾り）。

## MV（ユーザー提供の動画から解析）
- ユーザーがダウンロードしてリポジトリに置いた `videoplayback.mp4`（640x360、約194秒）をフレームごとに解析した（`data/video/sheet_*.jpg`）。
- 基準の一枚絵との差分を取り、大きく変わる区間は 0–4.5s（ロゴ）、155.5–157.3s、192–194s（ロゴ）の3つだけだった。
- 155.5s の赤い画面に「ドキュメントマチ」と表示される。これをEIDOLieのサイト内検索に入れると、ページ5へ進めた。
- 音声は解析していない。

## 使い方
```
chrome --headless=new --no-sandbox --remote-debugging-port=9222 --user-data-dir=.profile ...
python tools/play.py start | open <app> | search <kw> | click <text> | clickat x y | typeat x y <text> | scroll dy | login id pw | look
tools/p.sh ...        # ページの中身だけを表示
python tools/hint.py [ラベル...]   # 公式ヒントを別タブで開く（使用を記録）
```
