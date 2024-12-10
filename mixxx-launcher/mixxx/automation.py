import time
import logging
from typing import Dict, Optional
from pywinauto import Application, ElementNotFoundError


class MixxxAutomation:
    """
    Mixxxアプリケーションの自動化を行うクラス。

    UIオートメーションを使用して、Mixxxの各デッキからリアルタイムで情報を取得します。

    Attributes:
        app_title (str): 接続するアプリケーションのタイトル
        mixxx_window (object): Mixxxアプリケーションのウィンドウオブジェクト
        logger (logging.Logger): ログ出力用のロガーオブジェクト
        AUTOMATION_ELEM (Dict[str, str]): UIエレメントのオートメーションID辞書
    """

    def __init__(self, app_title: str = "Mixxx"):
        """
        MixxxAutomationクラスの初期化メソッド。

        Args:
            app_title (str, optional): 接続するアプリケーションのタイトル。デフォルトは"Mixxx"。
        """
        self.app_title = app_title
        self.main_window = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )

        self.AUTOMATION_ELEM: Dict[str, str] = {
            "Deck1_Title": "Deck1.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.TitleRow.WidgetGroup.TitleText",
            "Deck1_PlayPosition": "Deck1.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.TitleRow.AlignRight.PlayPositionText",
            "Deck1_Artist": "Deck1.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.ArtistRow.WidgetGroup.ArtistText",
            "Deck1_Duration": "Deck1.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.ArtistRow.AlignRight.DurationText",
            "Deck1_Bpm": "Deck1.WidgetGroup.RateContainer.BpmRateTapContainer.BpmTapContainer.AlignCenter.BpmText",
            "Deck1_Rate": "Deck1.WidgetGroup.RateContainer.BpmRateTapContainer.BpmTapContainer.AlignCenter.RateText",
            "Deck2_Title": "Deck2.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.TitleRow.WidgetGroup.TitleText",
            "Deck2_PlayPosition": "Deck2.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.TitleRow.AlignRight.PlayPositionText",
            "Deck2_Artist": "Deck2.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.ArtistRow.WidgetGroup.ArtistText",
            "Deck2_Duration": "Deck2.DeckRows12345.DeckRows234.WidgetGroup.WidgetGroup.DeckRow_2_3_ArtistTitleTime.ArtistRow.AlignRight.DurationText",
            "Deck2_Bpm": "Deck2.WidgetGroup.RateContainer.BpmRateTapContainer.BpmTapContainer.AlignCenter.BpmText",
            "Deck2_Rate": "Deck2.WidgetGroup.RateContainer.BpmRateTapContainer.BpmTapContainer.AlignCenter.RateText",
        }

    def connect(self, max_attempts: int = 3) -> bool:
        """
        Mixxxアプリケーションへの接続を試みる。

        指定された回数、アプリケーションへの接続を試行します。

        Args:
            max_attempts (int, optional): 接続試行の最大回数。デフォルトは3。

        Returns:
            bool: 接続に成功した場合True、失敗した場合False。
        """
        for attempt in range(max_attempts):
            try:
                app = Application(backend="uia").connect(
                    title=self.app_title, visible_only=True
                )
                self.main_window = app.window(title=self.app_title, visible_only=True)
                self.logger.info("Mixxxアプリケーションに接続しました")
                return True
            except Exception as e:
                self.logger.warning(f"接続試行 {attempt + 1}/{max_attempts} 失敗: {e}")
                time.sleep(1)

        self.logger.error("Mixxxアプリケーションに接続できませんでした")
        return False

    def update_element_cache(self) -> bool:
        """
        テキストエレメントを動的に更新する。

        Mixxxウィンドウ内のテキストエレメントを検索し、
        オートメーションID辞書を更新します。

        Returns:
            bool: エレメントの更新に成功した場合True、失敗した場合False。
        """
        if not self.main_window:
            if not self.connect():
                return False

        try:
            text_elements = self.main_window.descendants(control_type="Text")
            for elem in text_elements:
                for key, value in list(self.AUTOMATION_ELEM.items()):
                    if (
                        isinstance(value, str)
                        and value in elem.element_info.automation_id
                    ):
                        self.AUTOMATION_ELEM[key] = elem
            return True
        except Exception as e:
            self.logger.error(f"エレメントの更新中にエラー: {e}")
            return False

    def get_element_text(self, element_id: str, force_update: bool = False) -> str:
        """
        指定されたエレメントのテキストを取得する。

        Args:
            element_id (str): 取得するエレメントのID
            force_update (bool, optional): キャッシュを強制的に更新するかどうか。デフォルトはFalse。

        Returns:
            str: エレメントのテキスト。取得できない場合は空文字列。
        """
        if force_update:
            self.update_element_cache()

        element = self.AUTOMATION_ELEM.get(element_id)
        if element:
            if not isinstance(element, str):
                try:
                    return element.window_text()
                except Exception as e:
                    self.logger.error(
                        f"エレメント {element_id} のテキスト取得エラー: {e}"
                    )
            else:
                if force_update:
                    return ""

                return self.get_element_text(element_id, force_update=True)

        return ""


def main():
    """
    メインエントリーポイント。

    Mixxxアプリケーションの自動化を開始し、
    デッキ情報を継続的に表示します。
    """
    mixxx_automation = MixxxAutomation()

    while True:
        try:
            deck_info = {
                "Left": [
                    "Deck1_Title",
                    "Deck1_PlayPosition",
                    "Deck1_Artist",
                    "Deck1_Duration",
                    "Deck1_Bpm",
                    "Deck1_Rate",
                ],
                "Right": [
                    "Deck2_Title",
                    "Deck2_PlayPosition",
                    "Deck2_Artist",
                    "Deck2_Duration",
                    "Deck2_Bpm",
                    "Deck2_Rate",
                ],
            }

            for deck_name, elements in deck_info.items():
                print(f"{deck_name}:")
                for element_id in elements:
                    label = element_id.split("_")[-1]
                    value = mixxx_automation.get_element_text(element_id)
                    print(f"  {label:6}: {value}")
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nプログラムを終了します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break


if __name__ == "__main__":
    main()
