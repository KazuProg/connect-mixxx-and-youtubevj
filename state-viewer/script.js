"use strict";

window.addEventListener("load", (e) => {
  const eventSource = new EventSource("http://localhost:5000/events");

  eventSource.onmessage = onEventSourceMessage;

  eventSource.onerror = (err) => {
    console.error("SSE Error:", err);
  };

  requestAnimationFrame(updateTimeline);
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
    const ch = parseInt(data.group.substr(-2, 1));

    switch (data.control) {
      case "duration":
        document.querySelector(`#ch${ch} .duration`).innerText = formatTime(
          data.value
        );
        break;
      case "play":
        if (data.value === 1) {
          DATA[data.group]._playFrom = +new Date();
        }
        break;
      case "bpm":
        document.querySelector(`#ch${ch} .bpm`).innerText =
          data.value.toFixed(2);
        break;
      case "rate":
        DATA[data.group]._speed = 1 + -DATA[data.group].rateRange * data.value;
        document.querySelector(`#ch${ch} .bpm-rate`).innerText = (
          (DATA[data.group]._speed - 1) *
          100
        ).toFixed(2);
        break;
    }
  }

  if (data.group === "[Master]") {
    switch (data.control) {
      case "crossfader":
        document.querySelector("#crossfader").value = data.value;
        break;
    }
  }
}

function updateTimeline() {
  const updateChannel = (ch) => {
    const data = DATA[`[Channel${ch}]`];
    const deck = document.querySelector(`#ch${ch}`);

    if ("play" in data && data.play === 1) {
      const now = new Date();

      data.playposition +=
        (new Date() - data._playFrom) / (data.duration * 1000);

      if (1 < data.playposition) {
        data.playposition = 1;
      }

      data._playFrom = now;

      deck.querySelector(".position").style.width = `${
        data.playposition * 100
      }%`;

      deck.querySelector(".elapsed").innerText = formatTime(
        data.duration * data.playposition
      );

      deck.querySelector(".remaining").innerText = formatTime(
        data.duration * (1 - data.playposition)
      );
    }
  };

  updateChannel(1);
  updateChannel(2);

  document.querySelector("#debug").value = JSON.stringify(DATA, null, 2);

  requestAnimationFrame(updateTimeline);
}

function formatTime(sec) {
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60);
  const millis = Math.floor((sec % 1) * 1000);

  const formattedMinutes = String(minutes).padStart(2, "0");
  const formattedSeconds = String(seconds).padStart(2, "0");
  const formattedMillis = String(millis).padStart(3, "0");

  return `${formattedMinutes}:${formattedSeconds}.${formattedMillis}`;
}

function DebugView() {
  document.querySelector("#debug").style.display = "block";
}
