from datetime import datetime, timedelta, timezone

from app.sampler import main


def test_sampler_happy_path():
    start_date = (datetime.utcnow() - timedelta(days=1)).replace(tzinfo=timezone.utc)
    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)

    response = main(symbol='BTCUSDT', start_date=start_date, end_date=end_date)

    assert response > 100
