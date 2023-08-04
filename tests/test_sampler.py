from datetime import datetime, timedelta

from app.sampler import main


def test_sampler_happy_path():
    start_date = datetime.utcnow() - timedelta(days=1)

    response = main(symbol='SOLUSDT', start_date=start_date)

    assert response > 100
