import json
import requests
import threading
import time
from flask import (
    Flask,
    request,
    Response,
    send_file,
    send_from_directory,
    stream_with_context,
)
from flask_cors import CORS

from mixxx import MixxxProcessManager, MixxxAutomation, MixxxDatabase
from files import AudioFile

app = Flask(__name__, static_folder="html")
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
            threading.Thread(
                target=load_track_details, args=(data["group"],), daemon=True
            ).start()


def load_track_details(group):
    channel = group[-2]
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
            youtube_id = audio.get_tag("YouTubeID", True)

    value = {
        "group": group,
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
    # print(message)
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


@app.route("/youtube-vj/", defaults={"subpath": ""})
@app.route("/youtube-vj/<path:subpath>")
def proxy(subpath):
    if subpath == "assets/js/projection.js":
        return send_file("./html/projection.js", mimetype="text/javascript")

    # コントローラー画面は不要とする
    if subpath == "":
        subpath = "projection.html"

    proxied_url = f"https://kazuprog.github.io/youtube-vj/{subpath}"

    headers = {key: value for key, value in request.headers if key != "Host"}
    data = request.get_data()

    try:
        proxied_response = requests.request(
            method=request.method,
            url=proxied_url,
            allow_redirects=False,
        )
    except requests.RequestException as e:
        return f"Error occurred: {e}", 500

    essential_headers = {
        key: value
        for key, value in proxied_response.headers.items()
        if key in ["Content-Type", "Content-Length"]
    }

    content = proxied_response.content
    if subpath == "projection.html":
        content = content.decode(proxied_response.encoding or "utf-8").replace(
            "</head>",
            '  <script src="./assets/js/vj-controller.js"></script>\n  </head>',
        )

    response = Response(
        content,
        status=proxied_response.status_code,
        headers=essential_headers,
    )
    return response


# それ以外のすべてのルートでhtmlディレクトリのファイルを提供
@app.route("/<path:path>", methods=["GET"])
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)


# デフォルトでindex.htmlを返す場合（ルートや存在しないファイルにアクセスされた場合）
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # ファイルが見つからない場合、index.htmlを返す
        return send_from_directory(app.static_folder, "index.html")


def run_server():
    app.run(host="0.0.0.0", port=5000)


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
    threading.Thread(target=run_server, daemon=True).start()
    start_mixxx()
