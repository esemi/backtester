import os

from app.models import Position, OnHoldPositions

# шаг в абсолютных значениях для условия сделок.
step: float = 0.02

# шаг в процентах для условия сделок. 5% = 1.05
avg_rate_sell_limit: float = 1.05

# сколько позиций открываем в самом начале теста
init_buy_amount: int = 3

# сколько монет в одной позиции
continue_buy_amount: float = 1.0

# имя файла с ценой монеты, от старой к новой
rates_filename = 'BINANCE_SOLUSDT, 60.csv'


def main() -> None:
    history_rates = get_rates(rates_filename)
    open_positions: list[Position] = []
    closed_positions: list[Position] = []
    max_onhold_positions: OnHoldPositions | None = None

    for tick_number, tick_rate in enumerate(history_rates):
        print('tick', tick_number, tick_rate)

        on_hold_current = OnHoldPositions(
            amount=sum([pos.amount for pos in open_positions]),
            tick_number=tick_number,
            rate=tick_rate,
        )
        if not max_onhold_positions or max_onhold_positions.amount < on_hold_current.amount:
            max_onhold_positions = on_hold_current

        if not tick_number:
            print('init buy')
            for _ in range(init_buy_amount):
                open_positions.append(Position(
                    amount=continue_buy_amount,
                    open_rate=tick_rate,
                    open_tick_number=tick_number,
                ))
            continue

        if tick_number == 1:
            print('skip')
            continue

        # search position for sale
        avg_rate: float = (history_rates[tick_number - 2] + history_rates[tick_number - 1]) / 2
        print('search position for sell. Avg rate: {0}, tick rate: {1}'.format(avg_rate, tick_rate))

        sale_completed: bool = False
        for open_position_index, position in enumerate(open_positions):
            print(position)

            # условия на продажу
            # - средняя превысила цену покупки на 5%
            print('check sale by avg rate and open rate. Open rate +5% {0}. Average rate +5% {1}'.format(
                position.open_rate * avg_rate_sell_limit,
                avg_rate * avg_rate_sell_limit,
            ))
            if avg_rate >= position.open_rate * avg_rate_sell_limit:
                # - текущая цена выше чем средняя +5%
                if tick_rate >= avg_rate * avg_rate_sell_limit:
                    print('close position')
                    sale_position = open_positions.pop(open_position_index)
                    sale_position.close_rate = tick_rate
                    sale_position.close_tick_number = tick_number
                    closed_positions.append(sale_position)
                    sale_completed = True
                    break

            # - текущая цена выше цены покупки на 0.02+5%
            print('check sale by tick rate and open rate. Open rate + step + 5%: {0}'.format(
                position.open_rate * avg_rate_sell_limit + step,
            ))
            if tick_rate >= position.open_rate * avg_rate_sell_limit + step:
                print('close position')
                sale_position = open_positions.pop(open_position_index)
                sale_position.close_rate = tick_rate
                sale_position.close_tick_number = tick_number
                closed_positions.append(sale_position)
                sale_completed = True
                break

        if sale_completed:
            continue

        # вот смотри там где разница была больше или равно 0.02 мы закупали
        rate_go_down = history_rates[tick_number - 1] - tick_rate
        print('check rates for buy. Prev rate: {0}, diff {1}'.format(
            history_rates[tick_number - 1],
            rate_go_down,
        ))
        if rate_go_down >= step:
            print('open position')
            open_positions.append(Position(
                amount=continue_buy_amount,
                open_rate=tick_rate,
                open_tick_number=tick_number,
            ))

    _show_results(closed_positions, open_positions, last_rate=history_rates[-1], onhold=max_onhold_positions)


def get_rates(filename: str) -> list[float]:
    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'rates',
        filename,
    ))

    output: list[float] = []
    with open(filepath) as fd:
        for num, line in enumerate(fd):
            if not num or not line:
                continue

            output.append(float(line.split(',')[1]))
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
    )
    sell_amount = sum(
        [pos.close_rate * pos.amount for pos in closed_positions]
    )
    hold_amount = sum(
        [last_rate * pos.amount for pos in open_positions]
    )

    print('open positions', len(open_positions))
    print('closed positions', len(closed_positions))
    print(f'потратили на покупки монет {buy_amount}$')
    print(f'получили монет с продажи монет {sell_amount}$')
    print(f'сумма за ликвидацию зависших монет {hold_amount}$')

    buy_amount = buy_amount or 1.0
    print(f'доходность без учёта зависших монет: {(sell_amount - buy_amount) / buy_amount * 100}%')
    print(f'доходность с учётом зависших монет: {(sell_amount + hold_amount - buy_amount) / buy_amount * 100}%')

    if onhold:
        print(f'максимум монет на руках: {onhold.amount} монет на тике {onhold.tick_number} (курс {onhold.rate})')


if __name__ == '__main__':
    main()
