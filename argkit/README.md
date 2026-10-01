# argkit

ARG（Web上の探索型ミステリー）を、画面操作だけで攻略しながらログを取り、ダッシュボードにまとめる道具一式。

- `FORMAT.md` … ログのファイル構成と項目の仕様
- `tools/` … 操作・記録・集計のスクリプト
- `dashboard/template.html` … ダッシュボードのテンプレート（`build_report.py` がデータを埋め込む）
- `templates/` … 新しいゲームの雛形
- 手順書（Claude向け）… `../.claude/skills/arg-play/SKILL.md`

## 使い方

```bash
# 1. 新しいゲームを作る
argkit/tools/new_game.sh mygame "作品名" https://example.com/start https://example.com/hint

# 2. ブラウザを起動（別ターミナル／バックグラウンド）
argkit/tools/browser.sh mygame

# 3. 操作する（全部 mygame/data/actions.jsonl に残る）
python argkit/tools/play.py mygame start
python argkit/tools/play.py mygame click "ニュース"
python argkit/tools/play.py mygame search site "キーワード" --note "どこで見た語か"
python argkit/tools/play.py mygame typeat 835 185 "キーワード"
python argkit/tools/play.py mygame scroll 600

# 4. 記録を足す
python argkit/tools/log.py mygame page 5 title="記事" chapter="1章" method=site keyword="キーワード" source="#3の本文"
python argkit/tools/log.py mygame event human "ユーザーが動画を提供"
python argkit/tools/hint.py mygame --episode ① --why "次の語が分からない" "５" "ヒント1"
python argkit/tools/status.py mygame

# 5. ダッシュボード
python argkit/tools/build_report.py mygame       # → mygame/viz/index.html
```

必要なもの：Python 3 と `pip install playwright`、Chromium（`/opt/pw-browsers` のもの、または `CHROME=` で指定）、
証明書の取り込みに `certutil`（`apt-get install libnss3-tools`）。
