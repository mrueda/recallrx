const assert = require("node:assert/strict");
const test = require("node:test");

const { classifyFreshness } = require("../site/freshness.js");

const NOW = Date.parse("2026-07-29T12:00:00Z");

function hoursAgo(hours) {
  return new Date(NOW - (hours * 60 * 60 * 1000)).toISOString();
}

test("freshness remains current for less than 48 hours", function () {
  assert.equal(classifyFreshness(hoursAgo(47.99), NOW).state, "current");
});

test("freshness is delayed from 48 through 72 hours", function () {
  assert.equal(classifyFreshness(hoursAgo(48), NOW).state, "delayed");
  assert.equal(classifyFreshness(hoursAgo(72), NOW).state, "delayed");
});

test("freshness is stale beyond 72 hours", function () {
  assert.equal(classifyFreshness(hoursAgo(72.01), NOW).state, "stale");
});

test("freshness treats missing or invalid timestamps as stale", function () {
  assert.deepEqual(classifyFreshness(null, NOW), { state: "stale", ageHours: null });
  assert.deepEqual(classifyFreshness("not-a-date", NOW), { state: "stale", ageHours: null });
});
