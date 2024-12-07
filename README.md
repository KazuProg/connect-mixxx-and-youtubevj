# Connect Mixxx and YouTubeVJ

Mixxx と YouTube-VJ をうまく連携させて簡単に VDJ ができないか試行錯誤

いろいろ無理やり実装しているので、動作の保証はしません

## mixxx-controller-script

Mixxx のコントローラースクリプトから再生中の BPM やら長さやらを取得し、デバッグ出力経由で値を`mixxx-launcher`に送ってる

loopMIDI をインストールし、loopMIDI デバイスの Mapping としてスクリプトを読み込ませる

## mixxx-launcher

Mixxx を開発者モードで起動させ、`mixxx-controller-script`のデバッグ出力を SSE（Server-Sent Events）でクライアントへ送信

## state-viewer

`mixxx-launcher`から SSE を受信し、ブラウザに現在の情報を表示させるだけ
