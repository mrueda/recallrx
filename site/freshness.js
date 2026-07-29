(function (root, factory) {
  "use strict";

  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.RecallRxFreshness = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const HOUR_MS = 60 * 60 * 1000;

  function classifyFreshness(generatedAt, nowMs) {
    const generatedMs = Date.parse(generatedAt);
    const referenceMs = nowMs === undefined ? Date.now() : Number(nowMs);
    if (!Number.isFinite(generatedMs) || !Number.isFinite(referenceMs)) {
      return { state: "stale", ageHours: null };
    }

    const ageHours = Math.max(0, (referenceMs - generatedMs) / HOUR_MS);
    if (ageHours > 72) {
      return { state: "stale", ageHours: ageHours };
    }
    if (ageHours >= 48) {
      return { state: "delayed", ageHours: ageHours };
    }
    return { state: "current", ageHours: ageHours };
  }

  return { classifyFreshness: classifyFreshness };
});
