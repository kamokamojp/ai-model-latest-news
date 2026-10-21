# AIモデル最新情報ラジオ

AIモデルや関連機能の公式発表を、提供条件とともに確認する日本語ラジオの公開アーカイブです。この記事の日付は日本時間の確認日を表し、各提供元の発表日は一次資料に記された表記を保っています。

- 最新号（公式サイト）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/editions/2026-10-22
- 最新音声（MP3）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-22.mp3
- 予備音声（同一データのMP3コピー）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-22-backup.mp3
- 音声SHA-256: `8d0869dc9de792865e4f5a71422b7d6ff02c1757eab944df51444888842fd6b4`（1,931,084 bytes、両URLで同一）

## Repository layout

- `editions/`: 日付ごとの記事、公開HTML、台本MarkdownとJSON
- `production/`: 公式資料の調査記録、公開用の制作マニフェスト、再利用可能な日次ミラーワークフロー、該当号の制作コード
- `styles.css`, `app.js`: 公式号ページの表示と操作に使うソース

音声は重複保存せず、公式公開URLとハッシュで参照します。日次のIssue日付、一次資料、保存・検証の手順は `production/DAILY_WORKFLOW.md` を参照してください。過去号は保持し、同じ確認日の号を重複作成しません。
