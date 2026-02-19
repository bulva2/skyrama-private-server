# Import all command handlers explicitly
from .account_getLatest import handle_accountGetLatest
from .add_obj import handle_addObj
from .backgrounds_buy import handle_backgroundsBuy
from .backgrounds_makeCurrent import handle_backgroundsMakeCurrent
from .bays_buy import handle_baysBuy
from .buddy_accept import handle_buddyAccept
from .buddy_collectPassenger import handle_buddyCollectPassenger
from .buddy_decline import handle_buddyDecline
from .buddy_endRelationship import handle_buddyEndRelationship
from .buddy_getAll import handle_buddyGetAll
from .buddy_invite import handle_buddyInvite
from .buddy_receivePassengers import handle_buddyReceivePassengers
from .buddy_search import handle_buddySearch
from .cargoshops_buy import handle_cargoshopsBuy
from .cargoshops_buyCapacity import handle_cargoshopsBuyCapacity
from .cargoshops_buyCargo import handle_cargoshopsBuyCargo
from .cargoshops_collectSalesRevenue import handle_cargoshopsCollectSalesRevenue
from .cargoshops_fillShop import handle_cargoshopsFillShop
from .check_goals import handle_goal
from .crafting_buyMaterials import handle_craftingBuyMaterials
from .crafting_buySlot import handle_craftingBuySlot
from .crafting_collect import handle_craftingCollect
from .crafting_instant import handle_craftingInstant
from .crafting_processCraftingStep import handle_craftingProcessCraftingStep
from .crafting_start import handle_craftingStart
from .evoucher_book import handle_evoucherBook
from .flashCookies_set import handle_flashcookiesSet
from .general_getBuddyInitState import handle_getBuddyInitState
from .general_getConfig import handle_getConfig
from .general_getCv import handle_getCv
from .general_getInitState import handle_getInitState
from .general_soundIsOn import handle_soundIsOn
from .general_trackFlashError import handle_trackFlashError
from .goals_buyTask import handle_goalsBuyTask
from .handle_lucky_luggage_live import handle_lucky_luggage_live
from .hangars_buy import handle_hangarsBuy
from .hangars_upgrade import handle_hangarsUpgrade
from .landmarks_buy import handle_landmarksBuy
from .landmarks_makeCurrent import handle_landmarksMakeCurrent
from .landside_buildings_buy import handle_landsideBuildingsBuy
from .landside_buildings_harvest import handle_landside_buildingsHarvest
from .lucky_luggage_spin import handle_luckyLuggageSpin
from .map_extensions_buy import handle_mapExpansionsBuy
from .packages_buy import handle_packagesBuy
from .placeable_place import handle_placeablePlace
from .placeable_setInStorage import handle_placeableSetInStorage
from .planes_buy import handle_planesBuy
from .planes_createFlyBy import handle_planesCreateFlyBy
from .planes_get import handle_planesGet
from .planes_miss import handle_planesMiss
from .planes_onStartCargoTutorial import handle_planesOnStartCargoTutorial
from .planes_removeFlyByPlane import handle_planesRemoveFlyByPlane
from .planes_scrap import handle_planesScrap
from .planes_send import handle_planesSend
from .planes_sendback import handle_planesSendback
from .planes_sendbackflyby import handle_planesSendBackFlyBy
from .planes_setState import handle_planesSetState
from .planes_takeMeans import handle_planesTakeMeans
from .planes_upgrade import handle_planesUpgrade
from .playerdata_deleteBuddypingTime import handle_deleteBuddypingTime
from .playerdata_setbooster import handle_setbooster
from .playerdata_setLocation import handle_setLocation
from .playerdata_updateBuddypingTime import handle_updateBuddypingTime
from .playerdata_updateLevel import handle_playerdataUpdateLevel
from .playerdata_updateSettings import handle_updateSettings
from .recycling_collect import handle_recyclingCollect
from .recycling_instant import handle_recyclingInstant
from .recycling_start import handle_recyclingStart
from .resource_items_buy import handle_resourceItemsBuy
from .runways_buy import handle_runwaysBuy
from .sell import handle_sell
from .souvenirs_takeReward import handle_souvenirsTakeReward
from .special_buildings_buy import handle_specialBuildingsBuy
from .terminals_buy import handle_terminalsBuy

# Define what to export when "from commands import *" is used
__all__ = [
'handle_accountGetLatest',
    'handle_addObj',
    'handle_backgroundsBuy',
    'handle_backgroundsMakeCurrent',
    'handle_baysBuy',
    'handle_buddyAccept',
    'handle_buddyCollectPassenger',
    'handle_buddyDecline',
    'handle_buddyEndRelationship',
    'handle_buddyGetAll',
    'handle_buddyInvite',
    'handle_buddyReceivePassengers',
    'handle_buddySearch',
    'handle_cargoshopsBuy',
    'handle_cargoshopsBuyCapacity',
    'handle_cargoshopsBuyCargo',
    'handle_cargoshopsCollectSalesRevenue',
    'handle_cargoshopsFillShop',
    "handle_craftingBuyMaterials",
    "handle_craftingBuySlot",
    "handle_craftingCollect",
    "handle_craftingInstant",
    "handle_craftingProcessCraftingStep",
    "handle_craftingStart",
    'handle_deleteBuddypingTime',
    "handle_evoucherBook",
    'handle_flashcookiesSet',
    'handle_getBuddyInitState',
    'handle_getConfig',
    'handle_getCv',
    'handle_getInitState',
    'handle_goal',
    'handle_goalsBuyTask',
    'handle_hangarsBuy',
    'handle_hangarsUpgrade',
    'handle_landmarksBuy',
    'handle_landmarksMakeCurrent',
    'handle_landsideBuildingsBuy',
    'handle_landside_buildingsHarvest',
    'handle_luckyLuggageSpin',
    'handle_lucky_luggage_live',
    'handle_mapExpansionsBuy',
    'handle_packagesBuy',
    'handle_placeablePlace',
    'handle_placeableSetInStorage',
    'handle_planesBuy',
    'handle_planesCreateFlyBy',
    'handle_planesGet',
    'handle_planesMiss',
    'handle_planesOnStartCargoTutorial',
    'handle_planesRemoveFlyByPlane',
    'handle_planesScrap',
    'handle_planesSend',
    'handle_planesSendback',
    'handle_planesSendBackFlyBy',
    'handle_planesSetState',
    'handle_planesTakeMeans',
    'handle_planesUpgrade',
    'handle_playerdataUpdateLevel',
    "handle_recyclingCollect",
    "handle_recyclingInstant",
    "handle_recyclingStart",
    'handle_resourceItemsBuy',
    'handle_runwaysBuy',
    'handle_sell',
    'handle_setbooster',
    'handle_setLocation',
    'handle_soundIsOn',
    "handle_souvenirsTakeReward",
    'handle_specialBuildingsBuy',
    'handle_terminalsBuy',
    "handle_trackFlashError",
    'handle_updateBuddypingTime',
    'handle_updateSettings'
]
