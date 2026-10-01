---
name: arg-play
description: Play a web ARG (alternate reality game / 探索型ミステリー) through its visible UI only, log every action in the argkit format, and build the play-log dashboard. Use when the user asks to play, explore, solve or collect data on an ARG or web puzzle site, or to add another game to this repository.
---

# ARGを攻略して記録する

このリポジトリでは、ARGを「プレイヤーと同じ条件」で攻略し、その過程をデータとして残す。
ログの仕様は `argkit/FORMAT.md`、見本は `eidolie/`。

## 0. 準備

```bash
argkit/tools/new_game.sh <slug> "<作品名>" <開始URL> [<公式ヒントURL>]
argkit/tools/browser.sh <slug>          # バックグラウンドで実行（run_in_background）
python argkit/tools/play.py <slug> start
```

開いた画面を見て `<slug>/game.json` を埋める：`search_boxes`（検索窓のフレームとセレクタ）、
`miss_patterns`（「該当なし」の文言）、`progress_regex`（タイトルの進捗表示）、`total_pages`、`apps`（デスクトップ型なら）。
ここで確認のためにDOMを調べるのはよいが、ページの本文・答え・隠し要素は読まない。

## 1. 守ること（データの質に直結する）

- 画面に見えているものだけで解く。HTML/JSのソース、非表示要素、通信、ファイル一覧は見ない。
  見てしまったら即 `python argkit/tools/log.py <slug> event contamination "<何を見たか>"`。
- 人に助けてもらったら `log.py <slug> event human "<内容>"`。環境で詰まったら `event environment`。
- 外部への投稿（シェア、クリア登録、フォーム送信で外部に届くもの）はしない。
- 結果が分岐する操作・一度きりの操作の前に、ゲームのセーブ機能でセーブし `data/saves/` に置く。
- 公式ヒントは、自力で手詰まりになったときだけ、浅い見出しから1段ずつ開く：
  `python argkit/tools/hint.py <slug> --episode <id> --why "<詰まっている内容>" <見出し> [<小見出し> …]`
- ユーザーが「ネタバレなし」を望んでいるときは、報告に答えや固有名詞を書かない。

## 2. プレイのループ

1. `play.py <slug> look` で画面を読む。**画像はスクリーンショットを Read で必ず見る**。小さい写真・看板・腕時計・書類は拡大（クリックやトリミング）して読む。
2. 次の一手を決め、理由を `--note` に書く：
   `python argkit/tools/play.py <slug> search site "天城丈" --note "#16の『伊豆の踊子』の峠＋丈"`
3. 新しいページに着いたら注記する：
   `python argkit/tools/log.py <slug> page 17 title="週刊誌記事" chapter="マチ" method=site keyword="天城丈" source="#16 ファンサイトの謎かけ"`
4. 章が変わったら `log.py <slug> phase "<章名>"`。待ちが発生したら「◯◯待ち」の区間も作る。
5. ときどき `python argkit/tools/status.py <slug>` で未発見ページと最近の外れ語を確認する。
6. 区切りごとに `git add -A && git commit` して push する。

### 詰まったときの確認リスト（EIDOLieで実際に詰まった原因）

- 画像の中の文字（看板、写真の画面、手書き、伏字の書類）を読んだか。拡大できる画像はクリックしたか。
- 文字化け・エラー・空白に見える検索結果を、開かずに捨てていないか。
- 検索窓は複数ないか（ブラウザ検索とサイト内検索など）。検索は「1語・完全一致」ではないか。表記ゆれ（漢字・かな・大文字小文字・「附属/付属」）を試したか。
- 伏字（◯◯）は別ページの伏字と組み合わせられないか。
- 動画・音声など、この環境で再生できないメディアがないか。あればユーザーに相談する（フレーム解析や書き起こしの提供）。
- 送信・報告の手段が見つからないときは、別の場所（SNSのDM、ニュース）を見るとイベントが進むことがある。

## 3. プレイ後

1. `game.json` に `play_end` `result` `milestones` `activity_notes` `caveats` を書く。
2. `data/stuck.json`：ヒントを開いた場面ごとに `situation` と `breakthrough` を書く（外れ語とヒント本文は自動で入る）。ヒントなしで解いた謎は `solved` に。
3. `data/deps.json`：ページ間の想定ルートと関門（`gate`）を書く。
4. エンディングが複数あるなら、セーブからリプレイして `data/endings.json` にまとめる（EIDOLie の `tools/ending_run.py` が参考）。
5. `python argkit/tools/build_report.py <slug>` でダッシュボードを作り、目で確認してから Artifact として公開する。
