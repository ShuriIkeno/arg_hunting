# arg_hunting

- ARGを攻略・記録するときは `.claude/skills/arg-play/SKILL.md` の手順に従う。ログの仕様は `argkit/FORMAT.md`。
- 1ゲーム1ディレクトリ（`<slug>/`）。共通コードは `argkit/` に置き、ゲーム専用の一時スクリプトは `<slug>/tools/` に置く。
- ソースコードを読んで答えを得ない。読んでしまったら `events.jsonl` に `contamination` として残す。
- `.profile/`（ブラウザのプロファイル）はコミットしない。
