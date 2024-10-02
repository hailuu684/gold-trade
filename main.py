from numpy.array_api import float32
from telethon.sync import TelegramClient
import os
import asyncio
from place_trades import login_mt5_demo, mt5, place_trade, modify_stop_loss_to_entry
from cancel_trades import cancel_all_pending_orders
from secret_keys import api_id, api_hash
last_msg_id = None
title_name = 'goldtrades123456789'
short_name = 'goldtrades'

num_trial = '1'
# Create a new Telegram client
existed_path = f'E:\crypto\gold-trade\{num_trial}_trial.session'

# if os.path.exists(existed_path):
#     # Delete the file
#     os.remove(existed_path)
#
#     journal_path = f'E:\crypto\gold-trade\{num_trial}_trial.session-journal'
#     if os.path.exists(journal_path):
#         os.remove(journal_path)
#
#     print(f"{existed_path} has been deleted.")
#
#     client = TelegramClient(f'{num_trial}_trial', api_id, api_hash)
#     client.start()
#
# else:
client = TelegramClient(f'{num_trial}_trial', api_id, api_hash)
client.start()

channel_name = 'FVG_PrivateSignal'
channel_name_test = 'testgoldtrade'
session_name = f'my_session'

# Login account mt5 demo
account_info = login_mt5_demo()

stop_loss_modified = False


async def get_last_message():

    global last_msg_id
    global stop_loss_modified

    async with TelegramClient(session_name, api_id, api_hash) as client:
        # Fetch the channel entity (by username or ID)
        channel = await client.get_entity(channel_name)

        # Fetch the last message (limit=1 to get the latest message only)
        while True:
            async for message in client.iter_messages(channel, limit=1):
                # Check if the message starts with "PAIR: XAUUSD"
                if message.text and message.text.startswith("PAIR") and message.id != last_msg_id:

                    last_msg_id = message.id

                    # Parse the message to extract relevant details
                    lines = message.text.splitlines()
                    #
                    # Extract the pair (remove the # symbol if present)
                    pair = lines[0].split(":")[1].replace("#", "").strip()

                    # Extract the trade type
                    trade_type = lines[1].split(":")[1].strip().split()[0]  # Get only 'BUY' or 'SELL'

                    # Extract both entry prices from the same line
                    entries = lines[2].split(":")[1].strip().split()  # Split the entry values by space
                    entry_1 = float(entries[0].strip())
                    entry_2 = float(entries[1].strip())

                    # Extract the stop loss
                    stop_loss = float(lines[3].split(":")[1].strip())

                    # # Parse the message to extract relevant details
                    # lines = message.text.splitlines()
                    # pair = lines[0].split(":")[1].strip()
                    # trade_type = lines[1].split(":")[1].strip()
                    # entry_1 = float(lines[2].split(":")[1].replace(",", "").strip())
                    # entry_2 = float(lines[3].split(":")[1].replace(",", "").strip())
                    # stop_loss = float(lines[4].split(":")[1].replace(",", "").strip())

                    # print(trade_type)
                    # print(entry_1, entry_2)
                    # Determine pip adjustment based on trade type
                    pip_adjust = 0.1  # 1 pip is usually 0.1 for XAUUSD
                    gain_factors = [20, 40, 70, 100, 200]

                    if trade_type == 'BUY':
                        tps_1 = [entry_1 + (g * pip_adjust) for g in gain_factors]
                        tps_2 = [entry_2 + (g * pip_adjust) for g in gain_factors]
                    elif trade_type == 'SELL':
                        tps_1 = [entry_1 - (g * pip_adjust) for g in gain_factors]
                        tps_2 = [entry_2 - (g * pip_adjust) for g in gain_factors]
                    else:
                        raise ValueError(f"Unsupported trade type: {trade_type}")

                    # Symbol infor
                    symbol_info = mt5.symbol_info_tick("XAUUSD")._asdict()

                    if symbol_info is None:
                        print("Error: Could not retrieve symbol info")
                        return

                    # Current price
                    current_price = (symbol_info['bid'] + symbol_info['ask'])/2

                    account_balance = account_info['balance']

                    # Place trades for Entry 1 and Entry 2
                    place_trade(pair, trade_type, entry_1, stop_loss, tps_1, account_balance,
                                current_price=current_price)

                    place_trade(pair, trade_type, entry_2, stop_loss, tps_2, account_balance,
                                current_price=current_price)

                    # Print trade details for Entry 1
                    print(f"--- Trade Details for Entry 1 ---")
                    print(f"Pair: {pair}")
                    print(f"Type: {trade_type}")
                    print(f"Entry Price 1: {entry_1}")
                    print(f"Stop Loss: {stop_loss}")
                    for i, tp in enumerate(tps_1, start=1):
                        print(f"Take Profit {i}: {tp}")

                    # Print trade details for Entry 2
                    print(f"\n--- Trade Details for Entry 2 ---")
                    print(f"Pair: {pair}")
                    print(f"Type: {trade_type}")
                    print(f"Entry Price 2: {entry_2}")
                    print(f"Stop Loss: {stop_loss}")
                    for i, tp in enumerate(tps_2, start=1):
                        print(f"Take Profit {i}: {tp}")

                # Check if the last message is "+20pips" and stop loss modification has not been done
                if message.text and "+20pips" in message.text and not stop_loss_modified:
                    print("Received '+20pips' message, modifying stop loss to entry price.")

                    # Modify stop loss for all open trades for XAUUSD
                    modify_stop_loss_to_entry("XAUUSD")

                    # Set the flag to True to ensure the modification is only done once
                    stop_loss_modified = True

                    # Cancel all pre-orders (pending limit orders) for the XAUUSD pair
                    cancel_all_pending_orders("XAUUSD")

            # Check for new messages every 5 seconds
            await asyncio.sleep(5)


try:
    loop = asyncio.get_running_loop()
    task = loop.create_task(get_last_message())
    # await task

except RuntimeError:
    asyncio.run(get_last_message())

except KeyboardInterrupt:
    print("Keyboard Interrupt")
    mt5.shutdown()
