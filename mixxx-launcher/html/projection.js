"use strict";

/// Add
let ch = [];
/// Add

function init(fullscreen = false) {
  if (fullscreen) {
    const f =
      document.body.requestFullscreen ||
      document.body.webkitRequestFullscreen ||
      document.body.mozRequestFullScreen ||
      document.body.msRequestFullscreen;
    if (f) {
      f.call(document.body);
    }
  }
  document.querySelector("#init_button").remove();

  let ch0_opacity = 1;
  let ch1_opacity = 1;
  let crossfader = 0;

  /// Add
  const DATA = {
    "[Channel1]": {},
    "[Channel2]": {},
    "[Master]": {},
  };
  const eventHandlers = {
    onChangeVideo: (channel) => {
      ch[channel].pause();
      ch[channel].mute();
    },
  };
  /// Add

  /// Change VJPlayer to VJController
  const ch0 = new VJController(0, { events: eventHandlers });
  const ch1 = new VJController(1, { events: eventHandlers });
  /// Change

  /// Add
  ch.push(ch0);
  ch.push(ch1);

  const eventSource = new EventSource(`${location.origin}/events`);
  eventSource.onmessage = (event) => {
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
          crossfader = data.value;
          applyOpacity();
          break;
      }
    }
  };
  eventSource.onerror = (err) => console.error("SSE Error:", err);
  applyOpacity();
  ///Add

  ch0.addEventListener("dataApplied", (key, value) => {
    if (key === "filter" && "opacity" in value) {
      if (ch0_opacity == value.opacity) return;
      ch0_opacity = value.opacity;
      applyOpacity();
    }
  });
  ch1.addEventListener("dataApplied", (key, value) => {
    if (key === "filter" && "opacity" in value) {
      if (ch1_opacity == value.opacity) return;
      ch1_opacity = value.opacity;
      applyOpacity();
    }
  });

  window.addEventListener("storage", (event) => {
    if (event.key === "ytvj_sys") {
      systemHandler();
      return;
    }
    document.dispatchEvent(
      new CustomEvent("VJPlayerUpdated", {
        detail: {
          key: event.key,
          value: event.newValue,
        },
      })
    );
  });

  let _sysDat = {};
  function systemHandler() {
    const data = JSON.parse(localStorage.getItem("ytvj_sys"));

    for (const key in data) {
      if (JSON.stringify(_sysDat[key]) === JSON.stringify(data[key])) {
        continue;
      }
      _sysDat[key] = data[key];
      switch (key) {
        case "crossfader":
          crossfader = parseFloat(data[key]);
          applyOpacity();
          break;
      }
    }
  }

  systemHandler();

  function applyOpacity() {
    console.log("aaaa");
    const ch0_container = document.querySelector(`.player_container.ch0`);
    const ch1_container = document.querySelector(`.player_container.ch1`);

    const cf_weight = Math.abs(crossfader) / 2;
    const ch0_weight = ch0_opacity * (0.5 + (0 < crossfader ? 0 : cf_weight));
    const ch1_weight = ch1_opacity * (0.5 + (crossfader < 0 ? 0 : cf_weight));
    const ch0_isFront = ch0_weight >= ch1_weight;
    const ch1_isFront = ch1_weight > ch0_weight;
    ch0_container.style.zIndex = ch0_isFront ? 1 : 0;
    ch1_container.style.zIndex = ch1_isFront ? 1 : 0;
    ch0_container.style.opacity = ch0_weight == 0.5 ? 1 : ch0_weight;
    ch1_container.style.opacity = ch1_weight == 0.5 ? 1 : ch1_weight;
  }
}
