var YouTubeVJ = {};

YouTubeVJ.init = function () {
  print("YouTubeVJ initialized!");
  //engine.connectControl("[Channel1]", "beat_active", YouTubeVJ.update);

  engine.connectControl("[Channel1]", "track_loaded", YouTubeVJ.update);
  engine.connectControl("[Channel1]", "play", YouTubeVJ.update);
  engine.connectControl("[Channel1]", "bpm", YouTubeVJ.update);
  engine.connectControl("[Channel1]", "playposition", YouTubeVJ.update);
  engine.connectControl("[Channel1]", "beat_closest", YouTubeVJ.update);

  engine.connectControl("[Channel2]", "track_loaded", YouTubeVJ.update);
  engine.connectControl("[Channel2]", "play", YouTubeVJ.update);
  engine.connectControl("[Channel2]", "bpm", YouTubeVJ.update);
  engine.connectControl("[Channel2]", "playposition", YouTubeVJ.update);
  engine.connectControl("[Channel2]", "beat_closest", YouTubeVJ.update);

  engine.connectControl("[Master]", "crossfader", YouTubeVJ.update);
};

YouTubeVJ.shutdown = function () {
  print("YouTubeVJ shutting down.");
};

YouTubeVJ.update = function (value, group, control) {
  const sendValue = (group, control, value) => {
    print(
      "YouTubeVJ_Message:" +
        JSON.stringify({
          group,
          control,
          value: value || engine.getValue(group, control),
        })
    );
  };

  switch (`${group}.${control}`) {
    case "[Channel1].track_loaded":
    case "[Channel2].track_loaded":
      //sendValue(group, "duration");//ロード段階ではまだ取得できない？
      break;
    case "[Channel1].play":
    case "[Channel2].play":
      sendValue(group, "duration");
      sendValue(group, "playposition");
      break;
    case "[Channel1].bpm":
    case "[Channel2].bpm":
      sendValue(group, "rateRange");
      sendValue(group, "rate");
      break;
  }

  sendValue(group, control, value);
};
