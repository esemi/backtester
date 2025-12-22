import pickle
from decimal import Decimal

from app.models import Tick
from app.storage import get_saved_state, save_state, drop_state

test_state = {
    'test': [
        Tick(number=1, bid=Decimal(100499), ask=Decimal(100501), bid_qty=Decimal(100500), ask_qty=Decimal(100500))
    ]
}


def test_happy_path():
    state = pickle.dumps(test_state)

    save_state(state)
    response = get_saved_state('test:key')
    drop_state('test:key')

    decoded_state = pickle.loads(response)
    assert response == state
    assert decoded_state


def test_get_state_not_found():
    response = get_saved_state('invalid-key')

    assert response is None


def test_drop_state_not_found():
    assert get_saved_state('invalid-key') is None

    drop_state('invalid-key')
