# Import all command handlers explicitly
from .general_getCv import handle_getCv
from .general_soundIsOn import handle_soundIsOn
from .general_getConfig import handle_getConfig
from .general_getInitState import handle_getInitState
from .playerdata_setbooster import handle_setbooster
from .playerdata_setLocation import handle_setLocation
from .buddy_getAll import handle_buddyGetAll
from .planes_get import handle_planesGet
from .planes_setState import handle_planesSetState
from .placeable_place import handle_placeablePlace
from .planes_takeMeans import handle_planesTakeMeans
from .planes_sendback import handle_planesSendback
from .planes_buy import handle_planesBuy
from .account_getLatest import handle_accountGetLatest
from .planes_send import handle_planesSend
from .terminals_buy import handle_terminalsBuy
from .landside_buildings_harvest import handle_landside_buildingsHarvest
from .flashCookies_set import handle_flashcookiesSet
from .buddy_search import handle_buddySearch
from .buddy_invite import handle_buddyInvite
from .buddy_accept import handle_buddyAccept
from .playerdata_updateSettings import handle_updateSettings
from .planes_miss import handle_planesMiss
from .buddy_endRelationship import handle_buddyEndRelationship
from .buddy_decline import handle_buddyDecline
from .bays_buy import handle_baysBuy
from .runways_buy import handle_runwaysBuy
from .special_buildings_buy import handle_specialBuildingsBuy
from .placeable_setInStorage import handle_placeableSetInStorage
from .lucky_luggage_spin import handle_luckyLuggageSpin
from .landside_buildings_buy import handle_landsideBuildingsBuy
from .packages_buy import handle_packagesBuy
from .planes_upgrade import handle_planesUpgrade
from .planes_scrap import handle_planesScrap
from .goals_buyTask import handle_goalsBuyTask
from .playerdata_updateLevel import handle_playerdataUpdateLevel
from .planes_createFlyBy import handle_planesCreateFlyBy
from .planes_sendbackflyby import handle_planesSendBackFlyBy
from .planes_removeFlyByPlane import handle_planesRemoveFlyByPlane
from .planes_onStartCargoTutorial import handle_planesOnStartCargoTutorial
from .cargoshops_fillShop import handle_cargoshopsFillShop
from .cargoshops_collectSalesRevenue import handle_cargoshopsCollectSalesRevenue
from .general_getBuddyInitState import handle_getBuddyInitState
from .resource_items_buy import handle_resourceItemsBuy
from .playerdata_updateBuddypingTime import handle_updateBuddypingTime
from .playerdata_deleteBuddypingTime import handle_deleteBuddypingTime
from .cargoshops_buy import handle_cargoshopsBuy
from .cargoshops_buyCargo import handle_cargoshopsBuyCargo
from .cargoshops_buyCapacity import handle_cargoshopsBuyCapacity
from .evoucher_book import handle_evoucherBook
from .sell import handle_sell
from .backgrounds_buy import handle_backgroundsBuy
from .backgrounds_makeCurrent import handle_backgroundsMakeCurrent
from .landmarks_buy import handle_landmarksBuy
from .landmarks_makeCurrent import handle_landmarksMakeCurrent
from .hangars_upgrade import handle_hangarsUpgrade
from .map_extensions_buy import handle_mapExpansionsBuy
from .hangars_buy import handle_hangarsBuy
from .buddy_collectPassenger import handle_buddyCollectPassenger
from .handle_lucky_luggage_live import handle_lucky_luggage_live
from .check_goals import handle_goal
from .add_obj import handle_addObj
from .crafting_buySlot import handle_craftingBuySlot
from .crafting_start import handle_craftingStart
from .souvenirs_takeReward import handle_souvenirsTakeReward
from .crafting_buyMaterials import handle_craftingBuyMaterials
from .crafting_processCraftingStep import handle_craftingProcessCraftingStep
from .general_trackFlashError import handle_trackFlashError

# Define what to export when "from commands import *" is used
__all__ = [
    'handle_getCv',
    'handle_soundIsOn',
    'handle_getConfig',
    'handle_getInitState',
    'handle_setbooster',
    'handle_setLocation',
    'handle_buddyGetAll',
    'handle_planesGet',
    'handle_planesSetState',
    'handle_placeablePlace',
    'handle_planesTakeMeans',
    'handle_planesSendback',
    'handle_planesBuy',
    'handle_accountGetLatest',
    'handle_planesSend',
    'handle_terminalsBuy',
    'handle_landside_buildingsHarvest',
    'handle_flashcookiesSet',
    'handle_buddySearch',
    'handle_buddyInvite',
    'handle_buddyAccept',
    'handle_updateSettings',
    'handle_planesMiss',
    'handle_buddyEndRelationship',
    'handle_buddyDecline',
    'handle_baysBuy',
    'handle_runwaysBuy',
    'handle_specialBuildingsBuy',
    'handle_placeableSetInStorage',
    'handle_luckyLuggageSpin',
    'handle_landsideBuildingsBuy',
    'handle_packagesBuy',
    'handle_planesUpgrade',
    'handle_planesScrap',
    'handle_goalsBuyTask',
    'handle_playerdataUpdateLevel',
    'handle_planesCreateFlyBy',
    'handle_planesSendBackFlyBy',
    'handle_planesRemoveFlyByPlane',
    'handle_planesOnStartCargoTutorial',
    'handle_cargoshopsFillShop',
    'handle_cargoshopsCollectSalesRevenue',
    'handle_getBuddyInitState',
    'handle_resourceItemsBuy',
    'handle_updateBuddypingTime',
    'handle_deleteBuddypingTime',
    'handle_cargoshopsBuy',
    'handle_cargoshopsBuyCargo',
    'handle_cargoshopsBuyCapacity',
    'handle_sell',
    'handle_backgroundsBuy',
    'handle_backgroundsMakeCurrent',
    'handle_landmarksBuy',
    'handle_landmarksMakeCurrent',
    'handle_hangarsUpgrade',
    'handle_mapExpansionsBuy',
    'handle_hangarsBuy',    
    'handle_buddyCollectPassenger',
    'handle_lucky_luggage_live',
    'handle_goal',
    'handle_addObj',
    "handle_craftingBuySlot",
    "handle_craftingStart",
    "handle_evoucherBook",
    "handle_souvenirsTakeReward",
    "handle_craftingBuyMaterials",
    "handle_craftingProcessCraftingStep",
    "handle_trackFlashError"
]
