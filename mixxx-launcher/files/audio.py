import eyed3


class AudioFile:
    """
    AudioFileクラスは音声ファイル（例：MP3）からタグ情報を取得するためのクラスです。

    Attributes:
        file_path (str): 音声ファイルのパス。
        tags (dict): ファイルに含まれるタグ情報。

    Methods:
        load_tags():
            ファイルからタグを読み込み、tags属性に保存します。
        get_tag(key: str):
            指定されたタグキーの値を取得します。
        has_tag(key: str) -> bool:
            指定されたタグキーが存在するかを確認します。
    """

    def __init__(self, file_path: str):
        """
        初期化メソッド。音声ファイルのパスを設定します。

        Args:
            file_path (str): 音声ファイルのパス。
        """
        self.file_path = file_path
        self.tags = {}
        self.load_tags()

    def load_tags(self):
        """
        ファイルからタグを読み込み、tags属性に保存します。

        Raises:
            FileNotFoundError: ファイルが見つからない場合。
            ValueError: ファイルが無効な形式の場合。
        """
        self.tags = self._parse_frames_to_dict()

    def get_tag(self, key: str):
        """
        指定されたタグキーの値を取得します。

        Args:
            key (str): 取得するタグのキー。

        Returns:
            str or None: タグの値。キーが存在しない場合はNone。
        """
        return self.tags.get(key)

    def has_tag(self, key: str) -> bool:
        """
        指定されたタグキーが存在するかを確認します。

        Args:
            key (str): 確認するタグのキー。

        Returns:
            bool: キーが存在する場合はTrue、それ以外はFalse。
        """
        return key in self.tags

    def _parse_frames_to_dict(self):
        # フレームIDを意味のある名前に変換するマッピング
        frame_id_map = {
            "TALB": "album",
            "TPE1": "artist",
            "TBPM": "bpm",
            "COMM": "comments",
            "TCOM": "composer",
            "TCOP": "copyright",
            "TPOS": "part_of_set",
            "TSSE": "encoder",
            "TCON": "genre",
            "TKEY": "initial_key",
            "TSRC": "isrc",
            "TLAN": "language",
            "TIT2": "title",
            "TRCK": "track_number",
            "TYER": "year",
            "APIC": "attached_picture",
        }

        audio = eyed3.load(self.file_path)
        if not audio or not audio.tag:
            return {}

        frames_dict = {}

        for frame_id, frames in audio.tag.frame_set.items():
            readable_key = frame_id_map.get(
                frame_id.decode("utf-8"), frame_id.decode("utf-8")
            )

            if frame_id.decode("utf-8") == "TXXX":
                for frame in frames:
                    if hasattr(frame, "description") and hasattr(frame, "text"):
                        frames_dict[frame.description] = frame.text
            else:
                for frame in frames:
                    if hasattr(frame, "text"):
                        frames_dict[readable_key] = frame.text
                    elif hasattr(frame, "description") and hasattr(frame, "text"):
                        frames_dict[readable_key] = {
                            "description": frame.description,
                            "text": frame.text,
                        }
                    elif hasattr(frame, "date"):
                        frames_dict[readable_key] = frame.date
                    elif hasattr(frame, "image_data"):
                        frames_dict[readable_key] = "<Image Data>"
                    else:
                        frames_dict[readable_key] = "<Unsupported Frame Type>"

        return frames_dict


# 使用例
if __name__ == "__main__":
    file_path = "example.mp3"  # 対象の音声ファイルパスを指定

    try:
        import pprint

        audio = AudioFile(file_path)
        print("Title:", audio.get_tag("title"))
        print("Artist:", audio.get_tag("artist"))
        print("Tags:")
        pprint.pprint(audio.tags)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
