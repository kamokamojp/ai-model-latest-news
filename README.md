# AIモデル最新情報ラジオ

AIモデルや関連機能の公式発表を、提供条件とともに確認する日本語ラジオの公開アーカイブです。この記事の日付は日本時間の確認日を表し、各提供元の発表日は一次資料に記された表記を保っています。

第9号の確認日は2026年10月26日、予定時刻は08:00 JST、調査基準時は08:14:18 JSTです。Anthropicが10月25日UTCに記録した2件のClaude関連エラーは解決済みで、今回の確認時は公式ステータスが全コンポーネント稼働中でした。Volcengine Arkの文書にはKimi K3.1 Proのプラットフォーム別IDが掲載されていますが、日付のみの更新情報のため前号の締め切り後とは断定していません。選定した公式履歴の確認範囲は記事の調査記録に記載し、全世界の発表がないとは主張していません。

- 最新号（公式サイト）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/editions/2026-10-26.html
- 最新音声（MP3）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-26.mp3
- 予備音声（同一データのMP3コピー）: https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-26-backup.mp3
- 音声SHA-256: `deec094c4114790b2b14f4ec46080bef42f93660d74744630b281b4cb43b29fe`（1,268,972 bytes、両URLで同一。公開URLから確認済み）

## Repository layout

- `editions/`: 日付ごとの記事、公開HTML、台本MarkdownとJSON
- `production/`: 公式資料の調査記録、サニタイズ済み制作マニフェスト、再利用可能な日次ミラーワークフロー、該当号の制作コード
- `styles.css`, `app.js`: 公式号ページの表示と操作に使うソース

音声バイナリはGitHubに重複保存せず、公式サイトの公開URLとハッシュで参照します。日次のIssue日付、一次資料、保存・検証の手順は `production/DAILY_WORKFLOW.md` を参照してください。過去号は保持し、同じ確認日の号を重複作成しません。
