import pickle
from decimal import Decimal

from app.models import Tick
from app.storage import save_state, get_saved_state

test_state = {
    'test': [
        Tick(number=1, bid=Decimal(100499), ask=Decimal(100501))
    ]
}


def test_get_and_set_happy_path():
    state = pickle.dumps(test_state)

    save_state('test:key', state)
    response = get_saved_state('test:key')

    decoded_state = pickle.loads(response)
    assert response == state
    assert decoded_state


def test_get_state_not_found():
    response = get_saved_state('invalid-key')

    assert response is None
