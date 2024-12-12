import os
import sqlite3
from typing import Optional, List


class MixxxDatabase:
    """
    Mixxxデータベースから各種情報を取得するためのクラス。

    このクラスは、アーティストとタイトルに基づいて音楽トラックのファイルパスを
    検索するメソッドを提供します。
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Mixxxデータベース検索を初期化します。

        Args:
            db_path (Optional[str], optional): Mixxxデータベースへのカスタムパス。
            指定されない場合は、デフォルトのWindowsパスを使用します。
        """
        self.db_path = db_path or self._get_default_database_path()

    def _get_default_database_path(self) -> str:
        """
        Mixxxデータベースのデフォルトパスを取得します。

        Returns:
            str: デフォルトのMixxxデータベースファイルへの完全なパス
        """
        user_profile = os.environ.get("USERPROFILE")
        return os.path.join(user_profile, "AppData", "Local", "Mixxx", "mixxxdb.sqlite")

    def search_music(
        self, artist: str, title: str, like_search: bool = False
    ) -> Optional[int]:
        """
        Mixxxデータベース内で特定の音楽トラックを検索します。

        Args:
            artist (str): アーティスト名
            title (str): トラックのタイトル
            like_search (bool): 正規表現検索

        Returns:
            Optional[int]: トラックが見つかった場合はライブラリID、見つからない場合はNone
        """
        if not os.path.exists(self.db_path):
            print(f"データベースが存在しません: {self.db_path}")
            return None

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                if like_search:
                    query = """
                    SELECT id
                    FROM library
                    WHERE title LIKE ?
                      AND ( ? = "" and artist IS NULL
                         OR artist LIKE ?)
                    """
                else:
                    query = """
                    SELECT id
                    FROM library
                    WHERE title = ?
                      AND ( ? = "" and artist IS NULL
                         OR artist = ?)
                    """

                cursor.execute(query, (title, artist, artist))

                rows = cursor.fetchall()

                return rows[0][0] if rows else None

        except sqlite3.Error as e:
            print(f"SQLiteエラーが発生しました: {e}")
            return None

    def get_title(self, library_id: int) -> Optional[str]:
        """
        Mixxxデータベース内で特定の音楽トラックのタイトルを取得します。

        Args:
            library_id (int): ライブラリID

        Returns:
            Optional[str]: トラックが存在する場合は曲名、見つからない場合はNone
        """
        if not os.path.exists(self.db_path):
            print(f"データベースが存在しません: {self.db_path}")
            return None

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                query = "SELECT title FROM library WHERE id = ?"
                cursor.execute(query, (library_id,))

                rows = cursor.fetchall()

                return rows[0][0] if rows else None

        except sqlite3.Error as e:
            print(f"SQLiteエラーが発生しました: {e}")
            return None

    def get_artist(self, library_id: int) -> Optional[str]:
        """
        Mixxxデータベース内で特定の音楽トラックのアーティストを取得します。

        Args:
            library_id (int): ライブラリID

        Returns:
            Optional[str]: トラックが存在する場合はアーティスト名、見つからない場合はNone
        """
        if not os.path.exists(self.db_path):
            print(f"データベースが存在しません: {self.db_path}")
            return None

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                query = "SELECT artist FROM library WHERE id = ?"
                cursor.execute(query, (library_id,))

                rows = cursor.fetchall()

                return rows[0][0] if rows else None

        except sqlite3.Error as e:
            print(f"SQLiteエラーが発生しました: {e}")
            return None

    def get_location(self, library_id: int) -> Optional[str]:
        """
        Mixxxデータベース内で特定の音楽トラックのファイルパスを検索します。

        Args:
            library_id (int): ライブラリID

        Returns:
            Optional[str]: トラックが存在する場合はファイルパス、見つからない場合はNone
        """
        if not os.path.exists(self.db_path):
            print(f"データベースが存在しません: {self.db_path}")
            return None

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                query = """
                SELECT track_locations.location
                FROM library
                JOIN track_locations ON library.location = track_locations.id 
                WHERE library.id = ?
                """
                cursor.execute(query, (library_id,))

                rows = cursor.fetchall()

                return rows[0][0] if rows else None

        except sqlite3.Error as e:
            print(f"SQLiteエラーが発生しました: {e}")
            return None


def main():
    """
    MixxxDatabaseSearchクラスの機能のデモンストレーション。
    """
    # MixxxDatabaseSearchのインスタンスを作成
    mixxx_db = MixxxDatabase()

    # 特定のトラックを検索
    result = mixxx_db.search_music_path("Artist", "Title")
    if result:
        print(f"トラックのパス: {result}")
    else:
        print("トラックが見つかりませんでした。")

    # アーティストのすべてのトラックを検索
    artist_tracks = mixxx_db.search_all_tracks_by_artist("Artist")
    print("\nアーティストのすべてのトラック:")
    for track in artist_tracks:
        print(track)


if __name__ == "__main__":
    main()
