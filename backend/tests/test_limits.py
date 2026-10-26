from chatbot.limits import DailyQuota, RateLimiter


def test_daily_quota_allows_up_to_the_limit_then_refuses(tmp_path):
    quota = DailyQuota(limit=3, path=tmp_path / "usage.json", today=lambda: "2026-10-26")
    assert [quota.take() for _ in range(4)] == [True, True, True, False]


def test_daily_quota_resets_on_a_new_day(tmp_path):
    day = {"value": "2026-10-26"}
    quota = DailyQuota(limit=1, path=tmp_path / "usage.json", today=lambda: day["value"])
    assert quota.take() and not quota.take()
    day["value"] = "2026-10-27"
    assert quota.take()


def test_daily_quota_survives_a_restart(tmp_path):
    path = tmp_path / "usage.json"
    DailyQuota(limit=2, path=path, today=lambda: "2026-10-26").take()
    restarted = DailyQuota(limit=2, path=path, today=lambda: "2026-10-26")
    assert restarted.take() and not restarted.take()


def test_rate_limiter_is_per_ip():
    limiter = RateLimiter(per_minute=1)
    assert limiter.allow("1.1.1.1") and not limiter.allow("1.1.1.1")
    assert limiter.allow("2.2.2.2")
