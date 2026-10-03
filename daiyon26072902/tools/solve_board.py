"""復活の神経衰弱を解く(カードを1枚ずつめくり、見える絵柄をユーザーが目視した結果をmapで渡す方式ではなく、
全カードをめくって画面を保存→目視→ペア指定の2段階)。このスクリプトは1段階目: ページを開いて12枚を2枚ずつ撮影する。"""
import subprocess, sys
base="https://siosaigame.sakura.ne.jp/arg4/gisiki.html"
