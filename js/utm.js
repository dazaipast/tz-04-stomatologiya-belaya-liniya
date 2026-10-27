(function () {
  "use strict";

  var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content"];
  var params = new URLSearchParams(window.location.search);
  var hasUtm = keys.some(function (key) {
    return params.get(key);
  });

  if (hasUtm) {
    var fresh = {};
    keys.forEach(function (key) {
      var value = params.get(key);
      if (value) fresh[key] = value.slice(0, 200);
    });
    try {
      sessionStorage.setItem("bl_utm", JSON.stringify(fresh));
    } catch (error) {
      fresh = fresh;
    }
  }

  window.blUtm = function () {
    var stored = {};
    try {
      stored = JSON.parse(sessionStorage.getItem("bl_utm") || "{}");
    } catch (error) {
      stored = {};
    }
    return {
      utm_source: stored.utm_source || "direct",
      utm_medium: stored.utm_medium || "none",
      utm_campaign: stored.utm_campaign || "not_set",
      utm_content: stored.utm_content || "not_set"
    };
  };
})();
