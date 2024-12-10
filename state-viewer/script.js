"use strict";

window.addEventListener("load", (e) => {
  const eventSource = new EventSource("http://localhost:5000/events");

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
    const ch = parseInt(data.group.substr(-2, 1));
    const chData = DATA[`[Channel${ch}]`];
    const deck = document.querySelector(`#ch${ch}`);

    switch (data.control) {
      case "trackinfo":
        document.querySelector(`#ch${ch} .track-info .title`).innerText =
          data.value.title;
        document.querySelector(`#ch${ch} .track-info .artist`).innerText =
          data.value.artist;
        break;
      case "duration":
        document.querySelector(`#ch${ch} .duration`).innerText = formatTime(
          data.value
        );
        break;
      case "playposition":
        deck.querySelector(".position").style.width = `${
          chData.playposition * 100
        }%`;

        deck.querySelector(".elapsed").innerText = formatTime(
          chData.duration * chData.playposition
        );

        deck.querySelector(".remaining").innerText = formatTime(
          chData.duration * (1 - chData.playposition)
        );
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

function formatTime(sec) {
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60);

  const formattedMinutes = String(minutes).padStart(2, "0");
  const formattedSeconds = String(seconds).padStart(2, "0");

  return `${formattedMinutes}:${formattedSeconds}`;
}

function DebugView() {
  document.querySelector("#debug").style.display = "block";

  requestAnimationFrame(updateDebugData);
}

function updateDebugData() {
  document.querySelector("#debug").value = JSON.stringify(DATA, null, 2);

  requestAnimationFrame(updateDebugData);
}
