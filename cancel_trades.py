import MetaTrader5 as mt5


def cancel_all_pending_orders(pair):
    """
    Cancel all pending orders (limit orders) for the given symbol.
    """
    # Get all pending orders for the symbol (pair)
    pending_orders = mt5.orders_get(symbol=pair)

    if pending_orders is None:
        print(f"No pending orders found for {pair}.")
        return

    # Cancel each pending order
    for order in pending_orders:
        cancel_request = {
            "action": mt5.TRADE_ACTION_REMOVE,  # Action to remove the pending order
            "order": order.ticket  # Order ID (ticket) to cancel
        }

        # Send the request to cancel the order
        result = mt5.order_send(cancel_request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Pending order {order.ticket} canceled successfully.")
        else:
            print(f"Failed to cancel order {order.ticket}: {result.comment}")