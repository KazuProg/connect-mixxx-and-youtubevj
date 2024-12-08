import subprocess
import threading
import time
from flask import Flask, Response, stream_with_context
from flask_cors import CORS

mixxx_executable = r"C:\Program Files\Mixxx\Mixxx.exe"

app = Flask(__name__)
CORS(app)

connected_clients = []


def log_reader():
    """
    Mixxxの標準エラーログをリアルタイムに読み取り、接続されているクライアントに送信する。
    """
    # Mixxxを起動
    mixxx = subprocess.Popen(
        [mixxx_executable, "--developer"],
        stdout=subprocess.PIPE,  # 標準出力も取得（必要に応じて）
        stderr=subprocess.PIPE,  # 標準エラーを取得
        bufsize=1,  # 行単位でのバッファリング
        universal_newlines=True,  # テキストモードで読み込み
    )
    try:
        while True:
            log_msg = mixxx.stderr.readline().strip()

            if "YouTubeVJ_Message:" in log_msg:
                message = log_msg.split("YouTubeVJ_Message:", 1)[1].strip()
                broadcast_message(message)

            if log_msg == "" and mixxx.poll() is not None:
                break
    except Exception as e:
        print(f"Error reading logs: {e}")
    finally:
        mixxx.terminate()


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


if __name__ == "__main__":
    # Mixxxログ監視スレッドの開始
    threading.Thread(target=log_reader, daemon=True).start()
    app.run()
