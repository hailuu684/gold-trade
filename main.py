# from numpy.array_api import float32
from telethon.sync import TelegramClient
import os
import asyncio
from place_trades import login_mt5_demo, mt5, place_trade, modify_stop_loss_to_entry, login_real_account, \
    modify_tp_of_entry_1
from cancel_trades import cancel_all_pending_orders
from secret_keys import api_id, api_hash
from config import parameters
from send_tele_msg import send_telegram_message, send_tele_gram_message_test_1, send_tele_gram_message_GoProfit

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
# account_info = login_real_account(parameters)

ENTRY_1 = None
ENTRY_2 = None
TRADE_TYPE = None
TRADE_PAIR = None

stop_loss_modified = False
stop_loss_modified_tp_1 = False


async def get_last_message():
    global last_msg_id
    global stop_loss_modified
    global ENTRY_1
    global ENTRY_2
    global TRADE_TYPE
    global stop_loss_modified_tp_1
    global TRADE_PAIR

    async with TelegramClient(session_name, api_id, api_hash) as client:
        # Fetch the channel entity (by username or ID)
        channel = await client.get_entity(channel_name_test)  # channel_name_test, channel_name

        # Fetch the last message (limit=1 to get the latest message only)
        while True:
            symbol_info = mt5.symbol_info_tick("XAUUSD")._asdict()
            CURRENT_PRICE = (symbol_info['bid'] + symbol_info['ask']) / 2

            async for message in client.iter_messages(channel, limit=1):
                # Check if the message starts with "PAIR: XAUUSD"
                if message.text and message.text.startswith("PAIR") and message.id != last_msg_id:

                    try:
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

                        # Move to global
                        ENTRY_1 = entry_1
                        ENTRY_2 = entry_2
                        TRADE_TYPE = trade_type
                        TRADE_PAIR = pair

                        # Extract the stop loss
                        stop_loss = float(lines[3].split(":")[1].strip())


                        # # Forward telegram messages to other telegram group
                        # send_tele_gram_message_GoProfit(message.text)

                        # print(trade_type)
                        # print(entry_1, entry_2)
                        # Determine pip adjustment based on trade type
                        pip_adjust = parameters[pair]['pip_adjust']
                        gain_factors = parameters[pair]['gain_factors']

                        if trade_type == 'BUY':
                            tps_1 = [entry_1 + (g * pip_adjust) for g in gain_factors]
                            tps_2 = [entry_2 + (g * pip_adjust) for g in gain_factors]
                        elif trade_type == 'SELL':
                            tps_1 = [entry_1 - (g * pip_adjust) for g in gain_factors]
                            tps_2 = [entry_2 - (g * pip_adjust) for g in gain_factors]
                        else:
                            raise ValueError(f"Unsupported trade type: {trade_type}")

                        if symbol_info is None:
                            print("Error: Could not retrieve symbol info")
                            return

                        # Current price
                        current_price = (symbol_info['bid'] + symbol_info['ask']) / 2

                        account_balance = account_info['balance']

                        # Place trades for Entry 1 and Entry 2
                        place_trade(pair, trade_type, entry_1, stop_loss, tps_1, account_balance,
                                    current_price=current_price)

                        place_trade(pair, trade_type, entry_2, stop_loss, tps_2, account_balance,
                                    current_price=current_price)

                        stop_loss_modified = False

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

                    except (IndexError, ValueError) as e:
                        # If extraction fails, log the error and continue
                        print(f"Error extracting message details: {e}")
                        continue  # Skip this message and proceed to the next one

                # # Check if the last message is "+20pips" and stop loss modification has not been done
                # if message.text and "+20 Pips" in message.text and not stop_loss_modified:
                #     print("Received '+20pips' message, modifying stop loss to entry price.")
                #
                #     # Modify stop loss for all open trades for XAUUSD
                #     is_modified_success = modify_stop_loss_to_entry("XAUUSD")
                #
                #     # Set the flag to True to ensure the modification is only done once
                #     if is_modified_success:
                #         stop_loss_modified = True
                #
                #     # Cancel all pre-orders (pending limit orders) for the XAUUSD pair
                #     cancel_all_pending_orders("XAUUSD")

                # 1. Automatically send message and modify stl if 20 pips from entry 1 is reached
                # 2. Automatically set stl of entry to its price when reaches 20pips from entry 2
                if TRADE_TYPE == 'BUY':

                    # print('current_price = ', CURRENT_PRICE)
                    # print('condition = ', ENTRY_1 + 0.1*parameters[TRADE_PAIR]['gain_factors'][0])
                    # print('stop_loss_modified = ', stop_loss_modified)
                    # Do the 1st job
                    if CURRENT_PRICE >= ENTRY_1 + 0.1 * parameters[TRADE_PAIR]['gain_factors'][
                        0] and not stop_loss_modified:
                        # Modify stop loss for all open trades for XAUUSD
                        is_modified_success = modify_stop_loss_to_entry(TRADE_PAIR)

                        print('current_price = ', CURRENT_PRICE)
                        print('condition = ', ENTRY_1 + 0.1 * parameters[TRADE_PAIR]['gain_factors'][0])
                        print('stop_loss_modified = ', stop_loss_modified)

                        # Set the flag to True to ensure the modification is only done once
                        if is_modified_success:
                            stop_loss_modified = True

                        # Send message to telegram
                        # send_telegram_message(f"🟡 #{TRADE_PAIR} - {TRADE_TYPE}\n"
                        #                       "✅ +20 Pips  (Đang Có Lãi, AE Nên TP 1 Phần Lệnh Nhé)")

                        # send_tele_gram_message_GoProfit(f"🟡 #{TRADE_PAIR} - {TRADE_TYPE}\n"
                        #                                 "✅ +20 Pips  (Đang Có Lãi, AE Nên TP 1 Phần Lệnh Nhé)")

                    # Do the 2nd job
                    if CURRENT_PRICE <= ENTRY_2 and not stop_loss_modified_tp_1:
                        print(f"Current price {CURRENT_PRICE} has reached Entry 2: {ENTRY_2}, modifying TP of Entry 1.")
                        stop_loss_modified_tp_1 = modify_tp_of_entry_1(TRADE_PAIR, TRADE_TYPE, ENTRY_1)

                        if is_modified_success:
                            stop_loss_modified_tp_1 = True

                elif TRADE_TYPE == 'SELL':

                    # print('current_price = ', CURRENT_PRICE)
                    # print('condition = ', ENTRY_1 - 0.1 * parameters[TRADE_PAIR]['gain_factors'][0])
                    # print('stop_loss_modified = ', stop_loss_modified)

                    # Do the 1st job
                    if CURRENT_PRICE <= ENTRY_1 - 0.1 * parameters[TRADE_PAIR]['gain_factors'][
                        0] and not stop_loss_modified:

                        print('current_price = ', CURRENT_PRICE)
                        print('condition = ', ENTRY_1 - 0.1 * parameters[TRADE_PAIR]['gain_factors'][0])
                        print('stop_loss_modified = ', stop_loss_modified)

                        # Modify stop loss for all open trades for XAUUSD
                        is_modified_success = modify_stop_loss_to_entry(TRADE_PAIR)

                        # Set the flag to True to ensure the modification is only done once
                        if is_modified_success:
                            stop_loss_modified = True

                        # Send message to telegram
                        # send_telegram_message(f"🟡 #{TRADE_PAIR} - {TRADE_TYPE}\n"
                        #                       "✅ +20 Pips  (Đang Có Lãi, AE Nên TP 1 Phần Lệnh Nhé)")

                        # send_tele_gram_message_GoProfit(f"🟡 #{TRADE_PAIR} - {TRADE_TYPE}\n"
                        #                                 "✅ +20 Pips  (Đang Có Lãi, AE Nên TP 1 Phần Lệnh Nhé)")

                    # Do the 2nd job
                    if CURRENT_PRICE >= ENTRY_2 and not stop_loss_modified_tp_1:
                        print(f"Current price {CURRENT_PRICE} has reached Entry 2: {ENTRY_2}, modifying TP of Entry 1.")
                        stop_loss_modified_tp_1 = modify_tp_of_entry_1(TRADE_PAIR, TRADE_TYPE, ENTRY_1)

                        if is_modified_success:
                            stop_loss_modified_tp_1 = True

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
