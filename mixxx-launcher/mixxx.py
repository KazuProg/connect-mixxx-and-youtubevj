import subprocess

mixxx_executable = r"C:\Program Files\Mixxx\Mixxx.exe"


def start_with_log_handler(callback):
    """
    Mixxxを開発者モードで起動し、ログハンドラを設定して処理を行う。

    Args:
        callback (function): ログを処理するためのコールバック関数
    """
    mixxx = subprocess.Popen(
        [mixxx_executable, "--developer"],
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
    )

    try:
        for log_line in iter(mixxx.stderr.readline, ""):
            log_line = log_line.strip()

            if log_line:
                callback(log_line)

            if mixxx.poll() is not None:
                break
    except Exception as e:
        print(f"Error reading logs: {e}")
    finally:
        mixxx.terminate()
