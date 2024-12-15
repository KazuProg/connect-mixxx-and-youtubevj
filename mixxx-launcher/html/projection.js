"use strict";

let ch = [];

window.addEventListener("load", (e) => {
  const eventHandlers = {
    onChangeVideo: (channel) => {
      ch[channel].pause();
      ch[channel].mute();
    },
  };

  ch.push(new VJController(0, { events: eventHandlers }));
  ch.push(new VJController(1, { events: eventHandlers }));

  const eventSource = new EventSource(`${location.origin}/events`);

  eventSource.onmessage = onEventSourceMessage;

  eventSource.onerror = (err) => {
    console.error("SSE Error:", err);
  };

  setCrossfader(-1);
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
        break;
      case "play":
        if (data.value == 1) {
          targetCh.play();
        } else {
          targetCh.pause();
        }
        break;
      case "playposition":
        // 再生中のみシーク・同期させる
        if (chData.play === 1) {
          const pos = chData.duration * chData.playposition;

          if (0.1 < Math.abs(pos - targetCh.currentTime)) {
            targetCh.setTime(pos);
          }
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

function setCrossfader(cf_value) {
  const strength = 1 - Math.abs(cf_value);
  const ch0_container = document.querySelector(`.player_container.ch0`);
  const ch1_container = document.querySelector(`.player_container.ch1`);
  ch0_container.style.opacity = cf_value < 0 ? 1 : strength * 0.5;
  ch0_container.style.zIndex = cf_value < 0 ? 0 : 1;
  ch1_container.style.opacity = cf_value < 0 ? strength * 0.5 : 1;
  ch1_container.style.zIndex = cf_value < 0 ? 1 : 0;
}
