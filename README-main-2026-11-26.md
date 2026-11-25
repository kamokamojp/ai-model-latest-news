# AIモデル最新情報ラジオ — 第40号

公式一次資料を確認する日刊ラジオです。第40号（2026-11-26確認号）は、GitHub Pages版を正本とします。JetBrainsのMellum2.1 Instruct（11月25日付）、NIOのWorldModel 3.0（11月25日付）、Sand.aiのMAGI-2（11月24日付）、PrismMLのTernary Bonsai 2.5 27B（11月24日付）、MidjourneyのNiji 8（11月24日付）を整理しています。いずれも本シリーズ初掲載です。11月25日付の新しいモデル発表は2件、11月24日付は3件ありました。性能の数値は発表元の主張であり、独立検証ではありません。Mellum2.1 InstructのSWE-bench Verifiedの絶対スコアは、公式ブログに記載がなく、この号でも数値を記載していません。MAGI-2、Niji 8、Mellum2.1 Instructの公式記事には、取得したテキストに日付の記載がなく、発表日は同日付の報道などで確認したものとして記録しています。Niji 8については、日本時間の報道の中に発表を11月25日（日本時間）と書くものがあります。今回の確認は対象ページに限られ、全世界の新発表がなかったことを意味しません。

- [トップページ — 最新号とバックナンバー](https://kamokamojp.github.io/ai-model-latest-news/)
- [第40号 — 記事と台本](https://kamokamojp.github.io/ai-model-latest-news/editions/2026-11-26.html)
- [第40号の音声 — VOICEVOX Nemo MP3](https://kamokamojp.github.io/ai-model-latest-news/audio/2026-11-26.mp3)（SHA-256: `11849b6172ddb5bd58502e6b35481a08d40ea55415dadb82ad6f1999dbc65c44`、1,092,141 bytes）
- [第40号の予備音声](https://kamokamojp.github.io/ai-model-latest-news/audio/2026-11-26-backup.mp3)（主音声と同一ハッシュ）
- `editions/2026-11-26.md` — 記事
- `editions/2026-11-26-script.md` / `.json` — 台本と合成メタデータ
- `editions/2026-11-26.html` — 詳細ページ
- `production/2026-11-26-research.md` / `.json` — 調査範囲と基準時
- `production/2026-11-26-manifest.json` — 再現・QA・公開記録
- `editions/index.json` — 日付別号の索引。過去号を保持

## 調査・音声

調査基準時は2026-11-26 04:34 JST（2026-11-25T19:34:00Z）。予定確認時刻は08:00 JST。日付のみの発表には時刻やタイムゾーンを補っていません。発表ページに日付表示がない項目は、発表日を一次ページから断定しておらず、各社の掲載日・二次情報で記録しています。選定した公式資料に限る調査で、全世界を網羅したとは主張しません。音声はVOICEVOX Nemo 0.24.0のあかり（10005）・なおと（10001）、ノーマル・標準速度による合成です。サンプルと全編をffmpegでデコードし、主音声と予備音声のハッシュ一致を確認しました。人による実聴は行っていません。

[前号：2026年11月25日](https://kamokamojp.github.io/ai-model-latest-news/editions/2026-11-25.html)
