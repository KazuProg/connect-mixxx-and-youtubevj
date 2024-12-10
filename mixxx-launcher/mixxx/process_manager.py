import subprocess
import logging
import threading
from typing import Callable, Optional
from contextlib import contextmanager


class MixxxProcessManager:
    """
    Mixxxアプリケーションのプロセス管理を行うクラス。

    Mixxxを開発者モードで起動し、リアルタイムでログを処理するための機能を提供します。
    """

    def __init__(self, mixxx_path: Optional[str] = None):
        """
        MixxxProcessManagerのインスタンスを初期化。

        Args:
            mixxx_path (Optional[str]): Mixxxの実行可能ファイルのパス。
                                        デフォルトは標準的なインストール先。
        """
        self.mixxx_executable = mixxx_path or r"C:\Program Files\Mixxx\Mixxx.exe"
        self.logger = logging.getLogger(__name__)
        self._process: Optional[subprocess.Popen] = None
        self._log_thread = None
        self._stop_thread = threading.Event()
        self._log_callback: Optional[Callable[[str], None]] = self._default_log_callback

    def set_log_callback(self, callback: Callable[[str], None]):
        """
        ログ処理のコールバック関数を設定する。

        Args:
            callback (Callable[[str], None]): ログ行を処理するコールバック関数。
        """
        self._log_callback = callback

    @contextmanager
    def start(self):
        """
        コンテキストマネージャとしてMixxxを起動し、ログを処理するスレッドを開始する。

        Raises:
            subprocess.SubprocessError: プロセス起動または処理中にエラーが発生した場合
        """
        try:
            self._process = subprocess.Popen(
                [self.mixxx_executable, "--developer"],
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                text=True,
            )

            self._stop_thread.clear()
            self._log_thread = threading.Thread(target=self._log_reader, daemon=True)
            self._log_thread.start()

            yield
        except Exception as e:
            self.logger.error(f"ログ処理中にエラーが発生: {e}")
            raise
        finally:
            self._stop_thread.set()
            if self._log_thread and self._log_thread.is_alive():
                self._log_thread.join()
            self.stop()

    def is_process_running(self) -> bool:
        """
        プロセスが現在実行中かどうかを判定する。

        Returns:
            bool: プロセスが実行中の場合はTrue、終了している場合はFalse
        """
        if self._process is None:
            return False
        # プロセスがまだ実行中かどうかをpoll()でチェック
        return self._process.poll() is None

    def stop(self):
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

    def _log_reader(self):
        """ログを読み取るスレッドの処理"""
        try:
            assert self._process is not None
            for log_line in iter(self._process.stderr.readline, ""):
                if self._stop_thread.is_set():
                    break
                log_line = log_line.strip()
                if log_line:
                    self._log_callback(log_line)
        except Exception as e:
            self.logger.error(f"ログ読み取り中にエラーが発生: {e}")
        finally:
            self.logger.info("ログスレッドを終了しました")

    def _default_log_callback(self, log_line: str):
        """
        デフォルトのログコールバック。
        ログ行を標準のロギングシステムに送信する。

        Args:
            log_line (str): ログの1行
        """
        self.logger.info(f"Mixxx Log: {log_line}")


def main():
    """
    MixxxProcessManagerの使用例
    """
    import time

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
    )

    process_manager = MixxxProcessManager()

    def custom_log_processor(log_line: str):
        print(log_line)

    process_manager.set_log_callback(custom_log_processor)

    try:
        with process_manager.start():
            print("Mixxxが起動し、ログ処理を開始しました...")
            while process_manager.is_process_running():
                time.sleep(1)
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
