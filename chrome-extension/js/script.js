"use strict";

function injectScript(filePath) {
  const script = document.createElement("script");
  script.src = chrome.runtime.getURL(filePath);
  script.onload = function () {
    this.remove();
  };
  (document.head || document.documentElement).appendChild(script);
}

injectScript("js/page.js");
