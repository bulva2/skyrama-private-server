import time
import json
import os
import logging
from pathlib import Path

def handle_evoucherBook(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {"evoucher": {"success": False, "message": "General voucher error", "errorcode": 100}}
    voucher_code = request["p"]["code"].upper().strip()
    
    # Temporary solution, this isn't completely safe for production use
    p = Path(__file__).parents[1]
    voucher_file = os.path.join(p, "data", "voucher_codes.json.def")
    
    try:
        with open(voucher_file, "r", encoding="utf-8") as f:
            voucher_data = json.loads(f.read())

    except FileNotFoundError:
        logging.error("Voucher codes file not found!")
        rpcResult["r"]["evoucher"]["message"] = "Voucher system unavailable"
        rpcResult["r"]["evoucher"]["errorcode"] = 500
        return
    except json.JSONDecodeError:
        logging.error("Invalid voucher codes file format!")
        rpcResult["r"]["evoucher"]["message"] = "Voucher system error"
        rpcResult["r"]["evoucher"]["errorcode"] = 500
        return
    
    # Finds the voucher itself
    voucher = None
    voucher_index = -1
    for k, v in enumerate(voucher_data["vouchers"]):
        if v["code"] == voucher_code:
            voucher = v
            voucher_index = k
            break
    
    # Check for invalid code
    if not voucher:
        rpcResult["r"]["evoucher"]["message"] = "Invalid voucher code"
        logging.info(f"User {user_id} tried invalid voucher code: {voucher_code}")
        return
    
    # Check if voucher is still active
    if not voucher.get("active", True):
        rpcResult["r"]["evoucher"]["message"] = "This voucher code is no longer active"
        return

    # Check expiration date (Use UNIX time!)
    if voucher.get("expires", -1) != -1 and int(time.time()) > voucher["expires"]:
        rpcResult["r"]["evoucher"]["message"] = "This voucher code has expired"
        return

    # Check if the voucher hasn't reached its usage limit
    max_uses = voucher.get("max_uses", -1)
    if max_uses != -1 and voucher.get("current_uses", 0) >= max_uses:
        rpcResult["r"]["evoucher"]["message"] = "This voucher code has reached its usage limit"
        return

    # Initialize user's redeemed vouchers list if it doesn't exist
    if "redeemed_vouchers" not in json_data["playerData"]:
        json_data["playerData"]["redeemed_vouchers"] = []
    
    # Check if user has already redeemed this voucher
    if voucher_code in json_data["playerData"]["redeemed_vouchers"]:
        rpcResult["r"]["evoucher"]["message"] = "You have already redeemed this voucher code"
        return

    # Process rewards
    rewards = voucher.get("rewards", {})
    rewards_given = []
    
    # Currency rewards
    if "air_coins" in rewards and rewards["air_coins"] > 0:
        json_data["playerData"]["air_coins"] += rewards["air_coins"]
        rewards_given.append(f"{rewards['air_coins']} Air Coins")
    
    if "air_cash" in rewards and rewards["air_cash"] > 0:
        json_data["playerData"]["air_cash"] += rewards["air_cash"]
        rewards_given.append(f"{rewards['air_cash']} Air Cash")
    
    if "event_currency" in rewards and rewards["event_currency"] > 0:
        json_data["playerData"]["event_currency"] += rewards["event_currency"]
        rewards_given.append(f"{rewards['event_currency']} Event Currency")
    
    if "passengers" in rewards and rewards["passengers"] > 0:
        json_data["playerData"]["passengers"] += rewards["passengers"]
        rewards_given.append(f"{rewards['passengers']} Passengers")
    
    if "xp" in rewards and rewards["xp"] > 0:
        json_data["playerData"]["xp"] += rewards["xp"]
        rewards_given.append(f"{rewards['xp']} XP")
    
    if "super_fuel" in rewards and rewards["super_fuel"] > 0:
        json_data["playerData"]["super_fuel"] += rewards["super_fuel"]
        rewards_given.append(f"{rewards['super_fuel']} Super Fuel")
    
    # Mark voucher as redeemed by this user
    json_data["playerData"]["redeemed_vouchers"].append(voucher_code)
    
    # Update global usage count and save voucher file
    voucher_data["vouchers"][voucher_index]["current_uses"] = voucher.get("current_uses", 0) + 1
    try:
        with open(voucher_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(voucher_data, indent=2))

    except Exception as e:
        logging.error(f"Failed to update voucher usage count: {e}")
    
    # Success response
    rpcResult["r"]["evoucher"]["success"] = True
    rpcResult["r"]["evoucher"]["message"] = f"Voucher redeemed successfully! Received: {', '.join(rewards_given)}"
    rpcResult["r"]["evoucher"]["rewards"] = rewards_given
    rpcResult["r"]["evoucher"]["errorcode"] = 0

    logging.info(f"User {user_id} successfully redeemed voucher '{voucher_code}'.")

    