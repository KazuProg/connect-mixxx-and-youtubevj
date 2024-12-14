"use strict";

window.addEventListener("load", (e) => {
  const eventSource = new EventSource(`${location.origin}/events`);

  eventSource.onmessage = onEventSourceMessage;

  eventSource.onerror = (err) => {
    console.error("SSE Error:", err);
  };
});

const DATA = {
  "[Channel1]": {},
  "[Channel2]": {},
  "[Master]": {},
};

function onEventSourceMessage(event) {
  const data = JSON.parse(event.data);

  DATA[data.group][data.control] = data.value;

  if (data.group === "[Channel1]" || data.group === "[Channel2]") {
    const channel = parseInt(data.group.substr(-2, 1));
    const chData = DATA[`[Channel${channel}]`];
    const targetCh = ch[channel - 1];

    switch (data.control) {
      case "trackinfo":
        targetCh.setVideo(data.value.youtube_id);
        targetCh.mute();
        break;
      case "play":
        if (data.value == 1) {
          targetCh.resumePreview();
          targetCh.mute();
          targetCh.play();
        } else {
          targetCh.pause();
        }
        break;
      case "playposition":
        const pos = chData.duration * chData.playposition;

        if (0.1 < Math.abs(pos - targetCh.currentTime)) {
          targetCh.resumePreview();
          targetCh.setTime(pos);
        }
        break;
    }
  }

  if (data.group === "[Master]") {
    switch (data.control) {
      case "crossfader":
        setCrossfader(data.value);
        break;
    }
  }
}
