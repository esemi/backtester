import logging
import os

from app.models import Position, OnHoldPositions, Tick
from app.settings import app_settings
from app.strategy import Strategy

logger = logging.getLogger(__name__)


def main() -> None:
    strategy = Strategy()
    for tick in get_rates(app_settings.rates_filename):
        logger.info('tick {0}'.format(tick))

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading')
            break

    _show_results(
        strategy.closed_positions,
        strategy.open_positions,
        last_rate=strategy.get_ticks_history()[-1].price,
        onhold=strategy.max_onhold_positions,
    )


def get_rates(filename: str) -> list[Tick]:
    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'rates',
        filename,
    ))

    output: list[Tick] = []
    with open(filepath) as fd:
        tick_number = 0
        for num, line in enumerate(fd):
            if not num or not line:
                continue

            output.append(Tick(
                number=tick_number,
                price=float(line.split(',')[1]),
            ))
            tick_number += 1
    return output


def _show_results(
    closed_positions: list[Position],
    open_positions: list[Position],
    last_rate: float,
    onhold: OnHoldPositions | None,
) -> None:
    # считаем доходность
    buy_amount = sum(
        [pos.open_rate * pos.amount for pos in closed_positions]
    ) + sum(
        [pos.open_rate * pos.amount for pos in open_positions]
    )
    sell_amount = sum(
        [pos.close_rate * pos.amount for pos in closed_positions]
    )
    hold_amount = sum(
        [last_rate * pos.amount for pos in open_positions]
    )

    print('')
    print('Результаты тестирования:')
    print(f'открытых позиций на конец торгов {len(open_positions)}')
    print(f'закрытых позиций на конец торгов {len(closed_positions)}')
    print('')
    print('потратили на покупки монет $%.2f' % buy_amount)
    print('получили монет с продажи монет $%.2f' % sell_amount)
    print('сумма за ликвидацию зависших монет $%.2f' % hold_amount)
    print('')

    buy_amount = buy_amount or 1.0
    print('доходность без учёта зависших монет: %.2f%%' % ((sell_amount - buy_amount) / buy_amount * 100))
    print('доходность без учёта зависших монет: $%.2f' % (sell_amount - buy_amount))
    print('')
    print('доходность с учётом зависших монет: %.2f%%' % ((sell_amount + hold_amount - buy_amount) / buy_amount * 100))
    print('доходность с учётом зависших монет: $%.2f' % (sell_amount + hold_amount - buy_amount))

    if onhold:
        print('')
        print('максимум %.2f монет на руках на тике %d ($%.2f по курсу на этот тик, цена открытия $%.2f)' % (
            onhold.quantity,
            onhold.tick_number,
            onhold.tick_rate * onhold.quantity,
            onhold.buy_amount,
        ))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    main()
