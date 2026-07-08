import os
import re
import tempfile
import gradio as gr
from .pipeline import run_pipeline, CHANNEL_NAME
from .engine import THEMES
from .themes_jp import THEME_INFO_JP


def _safe_filename(name: str) -> str:
    name = name.encode("ascii", errors="replace").decode("ascii")
    name = re.sub(r'[\\/*?:"<>|\s]+', "_", name)
    name = name.strip("._")
    if not name:
        name = "audio"
    return name


def download_from_youtube(url: str) -> str:
    import yt_dlp
    tmpdir = tempfile.mkdtemp()
    out = os.path.join(tmpdir, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36",
        },
        "outtmpl": out,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception:
        ydl_opts["extractor_args"] = {}
        ydl_opts["http_headers"] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    for f in os.listdir(tmpdir):
        if f.endswith(".mp3"):
            src = os.path.join(tmpdir, f)
            safe_name = _safe_filename(f)
            dst = os.path.join(tmpdir, safe_name)
            if src != dst:
                os.rename(src, dst)
            return dst
    raise Exception("ダウンロード失敗: 音声ファイルが見つかりませんでした")


def process(audio_file, youtube_url, theme, orientation, start_offset, duration, progress=gr.Progress()):
    tmpdir = tempfile.mkdtemp()

    try:
        if youtube_url:
            progress(0, desc="YouTubeからダウンロード中…")
            audio_path = download_from_youtube(youtube_url)
        elif audio_file is not None:
            audio_path = audio_file
        else:
            return None, None, "### ❌ エラー\n音声ファイルをアップロードするか、YouTube URLを入力してください"

        result = run_pipeline(
            audio_path,
            theme=theme,
            output_dir=tmpdir,
            short_duration=duration,
            orientation=orientation,
            start_offset=start_offset,
            on_progress=lambda p, msg: progress(p, desc=msg),
        )

        video_path = result.get("video")
        thumb_path = result.get("thumbnail")

        ori_label = "横（16:9）" if orientation == "horizontal" else "縦（9:16）"
        summary = (
            f"### ✅ 完了！\n"
            f"**曲名:** {result['title']}\n"
            f"**BPM:** {result['bpm']}  |  **キー:** {result['key']}\n"
            f"**テーマ:** {result['theme']}  |  **向き:** {ori_label}\n"
            f"**長さ:** {duration}秒\n\n"
            f"ファイルは `{tmpdir}` に保存されました"
        )
        return video_path, thumb_path, summary

    except Exception as e:
        return None, None, f"### ❌ エラー\n```\n{e}\n```"


def create_ui():
    with gr.Blocks(title="RemixAI", theme=gr.themes.Soft()) as app:
        CH = "AI de Pon!"
        gr.HTML(
            f"""
            <div style="text-align:center;margin-bottom:8px;">
                <h1 style="font-size:2.5em;margin-bottom:0;background:linear-gradient(135deg,#00ff88,#ff00ff);
                           -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    🎵 RemixAI
                </h1>
                <p style="font-size:1.1em;color:#888;margin-top:4px;">
                    ♪ {CH} 〜曲を選んでテーマを選ぶだけ〜
                </p>
            </div>
            """
        )

        with gr.Tabs():
            with gr.TabItem("📁 ファイルから"):
                audio_input = gr.Audio(
                    type="filepath",
                    label="音声ファイルをアップロード",
                    sources=["upload"],
                )
                gr.Markdown("対応形式: MP3, WAV, FLAC, M4A, OGG")

            with gr.TabItem("🎬 YouTubeから"):
                youtube_url = gr.Textbox(
                    label="YouTube URL",
                    placeholder="https://youtube.com/watch?v=... を貼り付け",
                )

        # テーマ選択
        theme_dropdown = gr.Dropdown(
            choices=[(THEME_INFO_JP[t]["label"], t) for t in THEMES],
            value="original",
            label="リミックス・テーマ",
            interactive=True,
        )

        theme_preview = gr.HTML(value=_theme_html_jp("original"))

        def on_theme_change(theme):
            return _theme_html_jp(theme)

        theme_dropdown.change(
            fn=on_theme_change,
            inputs=[theme_dropdown],
            outputs=[theme_preview],
        )

        # 向き選択
        orientation_radio = gr.Radio(
            choices=[
                ("📱 縦（Short/Reels/TikTok）", "vertical"),
                ("🖥️ 横（通常YouTube）", "horizontal"),
            ],
            value="vertical",
            label="動画の向き",
        )

        with gr.Row():
            duration_slider = gr.Slider(
                minimum=15,
                maximum=120,
                value=30,
                step=5,
                label="動画の長さ（秒）",
            )
            start_slider = gr.Slider(
                minimum=0,
                maximum=300,
                value=0,
                step=5,
                label="開始位置（秒）",
            )

        generate_btn = gr.Button(
            "🚀 動画を生成",
            variant="primary",
            size="lg",
        )

        with gr.Row():
            with gr.Column(scale=1):
                video_output = gr.Video(
                    label="生成された動画",
                    width=360,
                    height=640,
                    autoplay=True,
                )
            with gr.Column(scale=1):
                thumbnail_output = gr.Image(
                    label="サムネイル",
                    width=360,
                    height=202,
                )

        status = gr.Markdown(
            "<div style='text-align:center;color:#888;padding:10px;'>"
            "音声をアップロードするか、YouTube URLを入力して「動画を生成」をクリック</div>"
        )

        generate_btn.click(
            fn=process,
            inputs=[
                audio_input, youtube_url,
                theme_dropdown, orientation_radio,
                start_slider, duration_slider,
            ],
            outputs=[video_output, thumbnail_output, status],
        )

        with gr.Accordion("💡 使い方・ヒント", open=False):
            gr.Markdown(
                """
                ### 使い方
                1. **音源を用意** — ファイル or YouTube URL
                2. **テーマ** — 雰囲気を選ぶ
                3. **向き** — 縦（Short）か横（通常動画）か
                4. **開始位置** — サビから始めたいときは秒数を指定
                5. **生成** — ポチッと待つだけ

                ### 出力
                - 縦: 1080×1920（YouTube Shorts / TikTok / Reels）
                - 横: 1920×1080（通常のYouTube動画）
                - 波形アニメーション + チャンネル名表示
                - サムネイルも自動生成

                ### バージョン情報
                RemixAI  v0.2  |  Channel: **AI de Pon!**
                """
            )

    return app


def _theme_html_jp(theme: str) -> str:
    info = THEME_INFO_JP.get(theme, THEME_INFO_JP["original"])
    color = info["color"]
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}22, {color}44);
        border: 2px solid {color};
        border-radius: 12px;
        padding: 16px;
        margin: 4px 0 12px 0;
    ">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="
                width: 32px; height: 32px;
                background: {color};
                border-radius: 50%;
                box-shadow: 0 0 20px {color}66;
            "></div>
            <div>
                <strong style="font-size:1.1em;">{info["label"]}</strong>
                <br>
                <span style="color:#999;font-size:0.9em;">{info["desc"]}</span>
            </div>
        </div>
    </div>
    """


def main(share: bool = False):
    app = create_ui()
    import asyncio

    if share:
        print("\n🌐 公開URLを生成中...（30秒ほど待ってね）", flush=True)

    result = app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share,
        inbrowser=not share,
        quiet=False,
    )

    if share:
        if isinstance(result, (list, tuple)):
            public_url = result[0] if result else ""
        elif isinstance(result, dict):
            public_url = result.get("share_url", "")
        else:
            public_url = str(result) if result else ""

        if public_url:
            with open(os.path.join(os.path.dirname(__file__), "..", "public_url.txt"), "w") as f:
                f.write(public_url)
            print(f"\n{'='*50}", flush=True)
            print(f"  🌐 公開URL: {public_url}", flush=True)
            print(f"  このURLを友達に教えてね！", flush=True)
            print(f"  ※ PCを起動してる間だけ有効", flush=True)
            print(f"{'='*50}", flush=True)


if __name__ == "__main__":
    main()
