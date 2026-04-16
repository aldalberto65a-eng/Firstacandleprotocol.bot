# ---------------- BREAKOUT (AGGRESSIVE) ---------------- #

if not state["breakout"]:
    if price > state["range_high"]:
        state["breakout"] = True
        send_message("⚡ BREAKOUT ABOVE RANGE")

    elif price < state["range_low"]:
        state["breakout"] = True
        send_message("⚡ BREAKOUT BELOW RANGE")

    return

# ---------------- EMA FILTER (LOOSENED) ---------------- #

if ema_value:
    # softer condition (not strict requirement anymore)
    if ema_value > state["range_high"] or ema_value < state["range_low"]:
        state["ema_ok"] = True
    else:
        # allow continuation anyway
        state["ema_ok"] = True

# ---------------- RETEST (AGGRESSIVE) ---------------- #

if state["breakout"] and state["ema_ok"] and ema_value:

    if abs(price - ema_value) < 0.5:
        send_message(
            f"📈 AGGRESSIVE SETUP\n"
            f"Price: {price}\n"
            f"EMA Retest Triggered"
        )

        state["breakout"] = False
        state["ema_ok"] = False


