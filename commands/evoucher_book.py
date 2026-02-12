import time
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.database import Voucher, VoucherRedemption, session_scope
from src.debug import report_issue

def handle_evoucherBook(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {"evoucher": {"success": False, "message": "General voucher error", "errorcode": 100}}
    voucher_code = request["p"]["code"].upper().strip()
    
    try:
        with session_scope() as session:
            # Find the voucher by code
            voucher = session.query(Voucher).filter_by(code=voucher_code).first()
            
            # Check for invalid code
            if not voucher:
                rpcResult["r"]["evoucher"]["message"] = "Invalid voucher code"
                logging.info(f"User {user_id} tried invalid voucher code: {voucher_code}")
                return
            
            # Check if voucher is still active
            if not voucher.active:
                rpcResult["r"]["evoucher"]["message"] = "This voucher code is no longer active"
                return

            # Check expiration date (Use UNIX time!)
            current_time = int(time.time())
            if voucher.expires is not None and current_time > voucher.expires:
                rpcResult["r"]["evoucher"]["message"] = "This voucher code has expired"
                return

            # Check if the voucher hasn't reached its usage limit
            if voucher.max_uses is not None and voucher.current_uses >= voucher.max_uses:
                rpcResult["r"]["evoucher"]["message"] = "This voucher code has reached its usage limit"
                return
            
            # Check if user has already redeemed this voucher
            already_redeemed = session.query(VoucherRedemption).filter_by(
                user_id=user_id,
                voucher_id=voucher.id
            ).first()
            
            if already_redeemed:
                rpcResult["r"]["evoucher"]["message"] = "You have already redeemed this voucher code"
                return

            # Process rewards
            rewards = voucher.rewards
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
            
            # Save redemption record
            redemption = VoucherRedemption(
                user_id=user_id,
                voucher_id=voucher.id
            )
            session.add(redemption)
            
            # Update global usage count
            if voucher.current_uses is not None:
                voucher.current_uses += 1
            
            # Success response
            rpcResult["r"]["evoucher"]["success"] = True
            rpcResult["r"]["evoucher"]["message"] = f"Voucher redeemed successfully! Received: {', '.join(rewards_given)}"
            rpcResult["r"]["evoucher"]["rewards"] = rewards_given
            rpcResult["r"]["evoucher"]["errorcode"] = 0

            logging.info(f"User {user_id} successfully redeemed voucher '{voucher_code}'.")
            
    # Apparently this happens if you try to redeem it twice in quick succession
    except IntegrityError:
        rpcResult["r"]["evoucher"]["message"] = "You have already redeemed this voucher code"
        report_issue("warning", f"User {user_id} attempted duplicate redemption of voucher code '{voucher_code}'")
        
    except SQLAlchemyError as e:
        logging.error(f"Database error during voucher redemption: {e}")
        rpcResult["r"]["evoucher"]["message"] = "Voucher system unavailable"
        rpcResult["r"]["evoucher"]["errorcode"] = 500
        
    except Exception as e:
        logging.error(f"Unexpected error during voucher redemption: {e}")
        rpcResult["r"]["evoucher"]["message"] = "Voucher system error"
        rpcResult["r"]["evoucher"]["errorcode"] = 500