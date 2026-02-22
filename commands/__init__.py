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

available_commands = {
    "account.getLatest": handle_accountGetLatest,
    "backgrounds.buy": handle_backgroundsBuy,
    "backgrounds.makeCurrent": handle_backgroundsMakeCurrent,
    "bays.buy": handle_baysBuy,
    "bays.sell": handle_sell,
    "buddy.accept": handle_buddyAccept,
    "buddy.collectPassenger": handle_buddyCollectPassenger,
    "buddy.decline": handle_buddyDecline,
    "buddy.endRelationship": handle_buddyEndRelationship,
    "buddy.getAll": handle_buddyGetAll,
    "buddy.invite": handle_buddyInvite,
    "buddy.receivePassengers": handle_buddyReceivePassengers,
    "buddy.search": handle_buddySearch,
    "cargoshops.buy": handle_cargoshopsBuy,
    "cargoshops.buyCapacity": handle_cargoshopsBuyCapacity,
    "cargoshops.buyCargo": handle_cargoshopsBuyCargo,
    "cargoshops.collectSalesRevenue": handle_cargoshopsCollectSalesRevenue,
    "cargoshops.fillShop": handle_cargoshopsFillShop,
    "crafting.buyMaterials": handle_craftingBuyMaterials,
    "crafting.buySlot": handle_craftingBuySlot,
    "crafting.collect": handle_craftingCollect,
    "crafting.instant": handle_craftingInstant,
    "crafting.processCraftingStep": handle_craftingProcessCraftingStep,
    "crafting.start": handle_craftingStart,
    "evoucher.book": handle_evoucherBook,
    "flashCookies.set": handle_flashcookiesSet,
    "general.getBuddyInitState": handle_getBuddyInitState,
    "general.getConfig": handle_getConfig,
    "general.getCv": handle_getCv,
    "general.getInitState": handle_getInitState,
    "general.soundIsOn": handle_soundIsOn,
    "general.trackFlashError": handle_trackFlashError,
    "goals.buyTask": handle_goalsBuyTask,
    "hangars.buy": handle_hangarsBuy,
    "hangars.upgrade": handle_hangarsUpgrade,
    "landmarks.buy": handle_landmarksBuy,
    "landmarks.makeCurrent": handle_landmarksMakeCurrent,
    "landside_buildings.buy": handle_landsideBuildingsBuy,
    "landside_buildings.harvest": handle_landside_buildingsHarvest,
    "landside_buildings.sell": handle_sell,
    "lucky_luggage.spin": handle_luckyLuggageSpin,
    "map_extensions.buy": handle_mapExpansionsBuy,        
    "packages.buy": handle_packagesBuy,
    "placeable.place": handle_placeablePlace,
    "placeable.setInStorage": handle_placeableSetInStorage,
    "planes.buy": handle_planesBuy,
    "planes.createFlyBy": handle_planesCreateFlyBy,
    "planes.get": handle_planesGet,
    "planes.miss": handle_planesMiss,
    "planes.onStartCargoTutorial": handle_planesOnStartCargoTutorial,
    "planes.removeFlyByPlane": handle_planesRemoveFlyByPlane,
    "planes.scrap": handle_planesScrap,
    "planes.send": handle_planesSend,
    "planes.sendback": handle_planesSendback,
    "planes.sendbackflyby": handle_planesSendBackFlyBy,
    "planes.setState": handle_planesSetState,
    "planes.takeMeans": handle_planesTakeMeans,
    "planes.upgrade": handle_planesUpgrade,
    "playerdata.deleteBuddypingTime": handle_deleteBuddypingTime,
    "playerdata.setbooster": handle_setbooster,
    "playerdata.setLocation": handle_setLocation,
    "playerdata.updateBuddypingTime": handle_updateBuddypingTime,
    "playerdata.updateLevel": handle_playerdataUpdateLevel,
    "playerdata.updateSettings": handle_updateSettings,
    "recycling.collect": handle_recyclingCollect,
    "recycling.instant": handle_recyclingInstant,
    "recycling.start": handle_recyclingStart,
    "resource_items.buy": handle_resourceItemsBuy,
    "runways.buy": handle_runwaysBuy,
    "runways.sell": handle_sell,
    "souvenirs.takeReward": handle_souvenirsTakeReward,
    "special_buildings.buy": handle_specialBuildingsBuy,
    "terminals.buy": handle_terminalsBuy,
    "terminals.sell": handle_sell,
}
