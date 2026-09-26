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

## 結果（2026-09-26）
- **END：A「EIDOLie is Alive」でクリア**（ベストエンド）。本編43/43ページとEXページの全部に到達した。
- プレイ時間：07:45〜10:24（約2時間40分。ツール作成とネットワーク設定の待ち時間を含む）
- 操作ログは1002件：検索278回、サイト内検索（typeat/sitesearch）157回、クリック244回、公式ヒントページの閲覧35回（中の項目を開いた回数を含む）
- やり直し：1回。V-Guardに50番を送ったところ「NO RESPONSE」だったため、セーブデータ（`data/saves/save_before_ending.dat`）をロードし、11番（「エールの歌」）を送り直した。
- エンディング分岐で取った行動の順番：V-Guardで励ます → 二階堂に依頼主と居場所を伝える → taskに反論（証拠：39番）→ 首謀者を報告
- 外部への送信（Xへのシェア、WebARGポータルへのクリア登録）はしていない。

### 人の助けを借りた部分
- MV：ユーザーが動画をダウンロードして提供した（YouTubeのボット判定のため、こちらでは取得できなかった）。フレーム解析はClaudeが行った。
- 歌詞：ユーザーが書き起こした（`data/video/lyrics_user.md`）。ゲーム内6番のページにも同じ歌詞がある。

### 公式ヒントを使った箇所
新人アドバイス、5、6、27（病院の看板）、37〜38（S-ID／パスワード）、39〜42、42以降（taskへの反論）、43、二階堂への回答、エンド分岐条件
