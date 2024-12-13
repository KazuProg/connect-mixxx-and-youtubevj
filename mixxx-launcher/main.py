import json
import threading
import time
from flask import Flask, Response, stream_with_context
from flask_cors import CORS

from mixxx import MixxxProcessManager, MixxxAutomation, MixxxDatabase
from files import AudioFile

app = Flask(__name__)
CORS(app)

connected_clients = []
mixxx_automation = None
mixxx_db = None


def handle_mixxx_log(log_line):
    if "YouTubeVJ_Message:" in log_line:
        message = log_line.split("YouTubeVJ_Message:", 1)[1].strip()
        broadcast_message(message)
        data = json.loads(message)
        if data["control"] == "track_loaded":
            channel = data["group"][-2]
            title = mixxx_automation.get_element_text(f"Deck{channel}_Title")
            artist = mixxx_automation.get_element_text(f"Deck{channel}_Artist")
            path = None
            youtube_id = None

            q_title = title
            if len(title) != 0 and title[-1] == "…":
                q_title = title.replace("…", "%")

            q_artist = artist
            if len(artist) != 0 and artist[-1] == "…":
                q_artist = artist.replace("…", "%")

            music_id = mixxx_db.search_music(q_artist, q_title, like_search=True)
            if music_id:
                title = mixxx_db.get_title(music_id)
                artist = mixxx_db.get_artist(music_id)
                path = mixxx_db.get_location(music_id)
                if path is not None:
                    audio = AudioFile(path)
                    youtube_id = audio.get_tag("YouTubeID")

            value = {
                "group": data["group"],
                "control": "trackinfo",
                "value": {
                    "title": title,
                    "artist": artist,
                    "path": path,
                    "youtube_id": youtube_id,
                },
            }
            broadcast_message(json.dumps(value))


def broadcast_message(message):
    """
    接続中の全てのクライアントにメッセージを送信する。
    """
    print(message)
    for client in connected_clients[:]:  # クライアントリストを安全に反復
        try:
            client["queue"].append(f"data: {message}\n\n")
        except Exception as e:
            print(f"Error broadcasting to client: {e}")
            connected_clients.remove(client)


@app.route("/events")
def sse():
    """
    クライアントが接続された時に呼び出されるSSEエンドポイント。
    """

    def event_stream(client):
        yield ": connected\n\n"  # 接続確認のため最初に送信
        while True:
            if client["queue"]:
                yield client["queue"].pop(0)  # キューからメッセージを送信
            else:
                yield ""  # 空のデータを送信して接続を維持
                time.sleep(0.1)

    # 新しいクライアントを追加
    client = {"queue": []}
    connected_clients.append(client)
    try:
        return Response(
            stream_with_context(event_stream(client)), content_type="text/event-stream"
        )
    finally:
        # クライアント切断時にリストから削除
        if client in connected_clients:
            # connected_clients.remove(client)
            print("Remove")


def start_mixxx():
    global mixxx_automation, mixxx_db
    mixxx_proc = MixxxProcessManager()
    mixxx_automation = MixxxAutomation()
    mixxx_db = MixxxDatabase()

    mixxx_proc.set_log_callback(handle_mixxx_log)

    try:
        with mixxx_proc.start():
            print("Mixxxが起動し、ログ処理を開始しました...")

            is_connected = False
            while not is_connected:
                is_connected = mixxx_automation.connect()
                if not is_connected:
                    time.sleep(5)

            while mixxx_proc.is_process_running():
                time.sleep(1)

    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    # Webサーバスレッドの開始
    threading.Thread(target=app.run, daemon=True).start()
    start_mixxx()
