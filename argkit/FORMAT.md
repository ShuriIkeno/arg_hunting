# ARG攻略ログのフォーマット

1つのゲームにつき1つのディレクトリを作り、次のファイルに記録する。
`argkit/tools/` のツールがほとんどを自動で書き、人やAIが手で足すのは「なぜそうしたか」の注記だけにする。
実例は `eidolie/`（EIDOLie、全44ページ・エンド6種）。

```
<slug>/
  game.json              ゲームの設定とレポート用の文言           手で書く（new_game.sh が雛形を作る）
  NOTES.md               推理メモ（自由記述）                     手で書く
  data/
    actions.jsonl        全操作のログ                            play.py / hint.py が自動で追記
    texts/               操作ごとの画面テキスト                   play.py が自動で保存
    screenshots/         操作ごとの画面                          play.py / hint.py が自動で保存
    hints.jsonl          読んだ公式ヒント                         hint.py が自動で追記
    events.jsonl         人の手助け・事前情報の混入・環境の制約     log.py event
    pages.json           ページ一覧と「どうやって見つけたか」       log.py page（found は自動）
    phases.json          章・区間（グラフの背景帯）                log.py phase / phase-end
    stuck.json           詰まった場面のまとめ                     プレイ後に手で書く
    deps.json            ページ間の依存関係（想定ルート）           プレイ後に手で書く
    endings.json         エンディングの比較                       プレイ後に手で書く（任意）
    endings/*.json       エンディングのリプレイ記録                ゲーム専用スクリプト（任意）
    saves/               ゲーム内のセーブデータ                    任意
  viz/index.html         ダッシュボード                          build_report.py が生成
```

時刻はすべてローカル時刻のISO 8601（秒まで、タイムゾーンなし）：`2026-09-26T07:45:29`。

## 守ること

- **画面に見えているものだけを使う。** ソースコード、非表示の要素、通信内容は読まない。読んでしまったら `events.jsonl` に `contamination` として残す。
- **人の手助けは必ず残す。** 動画の提供、音声の書き起こし、設定の変更などは `events.jsonl` に `human` として残す。
- **外部への投稿はしない。** 結果のシェアやクリア登録のボタンは押さない。
- **取り返しのつかない操作の前にセーブする。** ゲームにセーブ機能があれば `data/saves/` に保存し、`actions.jsonl` に `save` を残す。

---

## game.json

| キー | 型 | 説明 |
|---|---|---|
| `slug` | string | ディレクトリ名 |
| `title` | string | ダッシュボードの題（例：「EIDOLie 調査ログ」） |
| `game` / `publisher` | string | 作品名・制作者 |
| `url` | string | 開始URL（`play.py start` で開く） |
| `match_url` | string | ゲームのタブを見分ける部分文字列（省略時はドメイン） |
| `hint_url` | string | 公式ヒントページ（`hint.py` が使う） |
| `date` | string | プレイ日 |
| `lede` | string | ダッシュボード冒頭の説明文 |
| `total_pages` | number | 全ページ数（EX等を含む） |
| `page_note` | string | 全ページ数の補足（例：「本編43 + EX」） |
| `progress_regex` | string | タイトルからページ番号を抜き出す正規表現。グループ1が番号（例：`\[(\d+\|ex)/43\]`） |
| `title_selector` | string | ゲーム内のタイトル表示のCSSセレクタ（省略時は `document.title`） |
| `search_boxes` | object | 検索窓の定義。`{"名前": {"frame": "URLの一部", "selector": "CSS", "open_app": "apps のキー"}}` |
| `miss_patterns` | string[] | 「ヒットなし」を表す画面の文言（正規表現）。検索のヒット判定に使う |
| `apps` | object | デスクトップ型ゲームのアイコン名 `{"browser": "ブラウザ"}` |
| `methods` | object | ページの見つけ方の表示名。キーは `pages.json` の `method` |
| `nav_keywords` | string[] | 移動のためだけに打った定型の検索語（詰まり分析から除外） |
| `play_end` | string | 本編プレイの終了時刻。これより後の操作（リプレイ等）はグラフから外す |
| `result` | object | `{"end": "A", "title": "…", "label": "で調査完了"}` |
| `milestones` | object[] | 進捗グラフに入れる注記 `{"time", "label"}` |
| `activity_notes` | object[] | 検索回数グラフに入れる注記 `{"time", "label"}` |
| `stats_override` | object | 自動集計できない数字：`keyword_hits` `retries` `retries_note` |
| `text` | object | 文言の差し替え：`activity`（検索グラフの説明）、`deps_note`（関門表の補足） |
| `caveats` | string[] | 「データを読むときの注意」 |

## data/actions.jsonl（自動）

1行1操作。`play.py` が書く。

| キー | 説明 |
|---|---|
| `time` | 操作の時刻 |
| `cmd` | `start` `click` `clickat` `typeat` `type` `search` `select` `key` `scroll` `back` `open` `look` `shot` `hint` `save` `load` など |
| `arg` | コマンドの引数そのまま |
| `keyword` | 入力した語（`search` `type` `typeat` のとき） |
| `box` | 使った検索窓の名前（`search` のとき） |
| `hit` | 検索で何か出たか（`miss_patterns` で判定。判定できないときは無し） |
| `result` | `ok` / `NOT FOUND` / `ERROR …` / ログインの応答など |
| `title` | 操作後のゲーム内タイトル |
| `progress` | `title` から抜き出したページ番号 |
| `url` / `frames` | ページと、見えているフレームのURL |
| `screenshot` / `text` | `data/screenshots/` `data/texts/` のファイル名 |
| `note` | 任意。`--note` で付けた理由（「#16の『伊豆の踊子』から」など） |

EIDOLie の初期ログには `keyword` `hit` `progress` が無く、`browser_title` という旧キーがある。`build_report.py` は両方読める。

## data/hints.jsonl（自動）

| キー | 説明 |
|---|---|
| `time` | 開いた時刻 |
| `path` | クリックした見出しの列（例：`["２７", "ヒント２"]`） |
| `text` | そのとき新しく見えた本文。見出しだけなら `（見出しを開いただけ）` |
| `episode` | 対応する詰まり場面の id（`stuck.json`）。`--episode` で指定 |
| `why` | 何に詰まって開いたか（任意） |

## data/events.jsonl

| `type` | 使う場面 |
|---|---|
| `human` | 人が手伝った（動画の提供、書き起こし、ネットワーク許可） |
| `contamination` | プレイヤーが見ないはずの情報を見た（ソース、ファイル名、攻略情報） |
| `environment` | 環境の制約（通信遮断、ボット判定、再生できないメディア） |
| `note` | その他、時刻つきで残したいこと |

`{"time", "type", "text"}`

## data/pages.json

ページ（ゲームの進捗単位）ごとに1件。`log.py page <id> key=value …` で追記・更新する。

| キー | 説明 |
|---|---|
| `id` | ページ番号（文字列。`"EX"` なども可） |
| `title` | 短い名前 |
| `chapter` | 章（ページマップの行になる） |
| `found` | 初めて開いた時刻。空なら `actions.jsonl` の `progress` から自動で埋める |
| `method` | 見つけ方：`web`（ブラウザ検索）`site`（サイト内検索）`login`（ログイン・入力）`link`（リンク）。`game.json methods` で増やせる |
| `keyword` | 入力した語（リンクなら無し） |
| `source` | その語・リンクをどこで得たか（「#16 ファンサイトの『◯◯越え』」） |
| `hint` | 公式ヒントを見てから見つけたか |
| `human` | 人の手助けで見つけたか |

## data/phases.json

`[{"label": "マチ", "start": "…", "end": "…"}]`。進捗グラフの背景帯。待ち時間（「MV待ち」）も区間にしてよい。

## data/stuck.json（プレイ後）

```json
{
 "causes": {"image": {"label": "画像を読んでいなかった", "desc": "…"}},
 "episodes": [
  {"id": "②", "title": "アヤの章：病院が分からない", "start": "…", "end": "…", "cause": "image",
   "situation": "何が分からなかったか",
   "tried_from_log": true,
   "tried": ["自分で書く場合の外れ語"],
   "hint_episode": "②",
   "duration_note": "分",
   "breakthrough": "どう突破したか"}
 ],
 "solved": ["ヒントなしで解いた謎を1行ずつ"]
}
```

- `tried_from_log: true` にすると、`start` から最初のヒントまでに外れた検索語を `actions.jsonl` から自動で拾う。
- 「見たヒント」は `hints.jsonl` の `episode` が `hint_episode`（無ければ `id`）と一致するものを自動で並べる。
- 原因（`cause`）は自由に増やしてよい。今回使ったのは `image`（画像を見ていない）、`media`（見られないメディア）、`ignored`（違和感の見落とし）、`mechanics`（ゲームの仕組み）。

## data/deps.json（プレイ後）

ページ間の依存関係。「手がかり（item）」を介してページがつながる。

```json
{
 "items": {
  "kw_amagi": {"label": "「天城丈」", "from": ["16"], "gate": "『伊豆の踊子』の峠＝天城"},
  "kw_hyaku": {"label": "「百人一首」", "any": ["12", "14"]},
  "pw":       {"label": "パスワード", "from": ["8"], "gate": "「15と50」＝共通句"}
 },
 "deps": {"17": ["kw_amagi"], "38": ["sid", "pw", "partners"], "結末の行動": ["e_track"]},
 "end_nodes": ["結末の行動"],
 "end_titles": {"結末の行動": "説明"},
 "focus": "38",
 "note": "依存関係の組み方についての補足"
}
```

- `from` はすべて必要、`any` はどれか1つでよい。`from: []` は最初から持っている情報。
- `gate` を書いた item は「関門」として、解けなかった場合にどこで止まるかを自動計算する。
- 実際のプレイ順ではなく、作者が想定した経路で組む。

## data/endings.json（任意）

```json
{
 "intro": "…", "total_ends": 6,
 "ends": {"A": {"title": "…", "tone": "good|bad|gray", "fate": "結末の一言"}},
 "columns": {"param": "変えた条件の列名", "name": "報告の列名", "fate": "結末の列名"},
 "tree": [{"cond": "条件（<b>可</b>）", "end": "F"}, {"cond": "どれにも当てはまらない", "end": "A", "default": true}],
 "runs": [{"label": "A", "param": "11番", "steps": ["励ます", "伝える"], "name": "…", "end": "A", "surprise": false}],
 "notes": ["…"],
 "route": {"title": "エンドAまでの手順", "intro": "…", "steps": [{"time": "10:01", "label": "セーブ", "desc": "…", "state": "ok|fail"}]}
}
```

## ダッシュボード

```
python argkit/tools/build_report.py <slug>          # → <slug>/viz/index.html
```

`stuck.json` `deps.json` `endings.json` が無ければ、その節は表示されない。
