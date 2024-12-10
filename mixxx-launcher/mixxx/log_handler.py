import subprocess
import logging
from typing import Callable, Optional
from contextlib import contextmanager


class MixxxLogHandler:
    """
    Mixxxアプリケーションのログハンドリングを管理するクラス。

    Mixxxを開発者モードで起動し、リアルタイムでログを処理するための機能を提供します。
    """

    def __init__(self, mixxx_path: Optional[str] = None):
        """
        MixxxLogHandlerのインスタンスを初期化。

        Args:
            mixxx_path (Optional[str]): Mixxxの実行可能ファイルのパス。
                                        デフォルトは標準的なインストール先。
        """
        self.mixxx_executable = mixxx_path or r"C:\Program Files\Mixxx\Mixxx.exe"
        self.logger = logging.getLogger(__name__)
        self._process: Optional[subprocess.Popen] = None

    @contextmanager
    def start_with_log_handler(self, callback: Optional[Callable[[str], None]] = None):
        """
        コンテキストマネージャとしてMixxxを起動し、ログを処理する。

        Args:
            callback (Optional[Callable[[str], None]], optional):
                ログ行を処理するコールバック関数。未指定の場合は標準ロギングを使用。

        Raises:
            subprocess.SubprocessError: プロセス起動または処理中にエラーが発生した場合
        """
        default_callback = self._default_log_callback if callback is None else callback

        try:
            self._process = subprocess.Popen(
                [self.mixxx_executable, "--developer"],
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                text=True,
            )

            for log_line in iter(self._process.stderr.readline, ""):
                log_line = log_line.strip()
                if log_line:
                    default_callback(log_line)

                if self._process.poll() is not None:
                    break

            yield
        except Exception as e:
            self.logger.error(f"ログ処理中にエラーが発生: {e}")
            raise
        finally:
            self._terminate_process()

    def _default_log_callback(self, log_line: str):
        """
        デフォルトのログコールバック。
        ログ行を標準のロギングシステムに送信する。

        Args:
            log_line (str): ログの1行
        """
        self.logger.info(f"Mixxx Log: {log_line}")

    def _terminate_process(self):
        """
        Mixxxプロセスを安全に終了する。
        """
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            finally:
                self._process = None


def main():
    """
    MixxxLogHandlerの使用例
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
    )

    log_handler = MixxxLogHandler()

    def custom_log_processor(log_line: str):
        print(log_line)

    try:
        with log_handler.start_with_log_handler(callback=custom_log_processor):
            print("Mixxxが起動し、ログ処理を開始しました...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
