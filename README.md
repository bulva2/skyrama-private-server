# Skyrama Private Server

Skyrama Private Server is an attempt to create a custom server for Skyrama, a Bigpoint game. Not all features have been implemented, and those that are likely contain bugs. All help is welcome!

Keep in mind that although passwords should be properly encrypted/hashed, it is recommended to not use a password you use for any other services.

## Legal Notice / DMCA

This repository is made for educational and archival purposes only and will not be monetized in any way. We are NOT affiliated nor sponsored by Bigpoint GmbH. All game content, imagery, and trademarks are the property of Bigpoint GmbH. This project is not meant to replace Skyrama in any way. Please contact us for any legal problems, and we'll quickly take appropriate action. You can contact the repository owner on this Discord server: https://discord.gg/uFhJRvggZy.

## How to play

You will either need a browser that supports Flash (and Flash Player itself). We do NOT have own launcher so we cannot vouch fully for any available options but we have a good experience with:
- Older Chromium with Flash Player installed:
[Older Chromium 82](https://cdn.discordapp.com/attachments/1422989171009654804/1469480781263929354/chromium-82-0-4050.zip?ex=698878df&is=6987275f&hm=25f577b9b57b065f6d8bc25e3bd661461de0c9dcfb53d86675f1ce7f55663b41&)
[Compatible Flash Player](https://cdn.discordapp.com/attachments/1422989171009654804/1469480781679427616/flashplayer32_0r0_371_winpep_debug.exe?ex=698878df&is=6987275f&hm=4f1a4562d2445bf20d2606f7a79e385a166b9d25d2ef05243465821be319f9d4&)
- Standalone Flash Browser, no Flash Player required (may contain ads):
[Flash Browser](https://github.com/radubirsan/FlashBrowser/releases/download/v0.81/v0.81_FlashBrowser_x64.exe).

## Where can I try it out?

We currently host our own test server here: https://crimson-goat-16936.zap.cloud/
The server may be down anytime for maintenance or updates, use different login/password than you use in skyrama!

Also join us on [Discord](https://discord.gg/uFhJRvggZy)!

## How to run the code locally

1. Obtain Skyrama .swf file, we cannot provide this on GitHub
2. Place Skyrama .swf file into assets folder
3. Install PostgreSQL and create a database
4. Change the database connection uri in config.cfg
5. Run setup_database.py
6. Run scripts\setup.bat (.sh)
7. Run scripts\start.bat (.sh)
8. Enjoy!

## Known issues
- Some anticheat checks are currently incorrectly set-up
- Buying hangar and upgrading it right away may cause a crash
- Recycling Center isn't implemented
- Some daily quest may be incorrectly setup
- Probably much more xD

## List of quest task types
These are all the types of tasks that can be in a quest. Doing an unimplemented one will work in-game, but after refreshing all further progress on quests will be gone! The tutorial (as well as the mid-game "cargo tutorial") and most important other types are working as well.

- [x] BuyBay
- [x] BuyLandsideBuilding
- [x] BuyPlane
- [x] CollectSouvenir
- [x] FillShop
- [x] GetAirCoins
- [x] GetCargo
- [x] GetPassengers
- [x] LandPlane
- [x] PlaceBay
- [x] PlaceCargoshop
- [ ] PlaceDecoration
- [x] PlaceLandsideBuilding
- [x] PlaceTerminal
- [x] PlaceWarehouse
- [x] QuickStartPlane
- [x] ReturnPlane
- [x] SellProducts
- [x] SendPlane
- [ ] SendPlaneToStranger
- [ ] StoreLandsideBuilding
- [ ] StoreTerminal

## List of game commands
I'm not 100% sure if all of these are still being used in the latest version of Skyrama, but I hope it gives an indication of the progress of this private server.

- [x] general.getCv
- [x] general.getConfig
- [x] playerdata.updateBuddypingTime
- [x] playerdata.deleteBuddypingTime
- [x] account.getLatest
- [x] general.getInitState
- [x] general.soundIsOn
- [x] general.getBuddyInitState
- [x] playerdata.setLocation
- [x] playerdata.updateLevel
- [x] playerdata.updateSettings
- [x] evoucher.book
- [x] lucky_luggage.spin
- [x] buddy.getAll
- [x] buddy.collectPassenger
- [ ] buddy.receivePassengers - Not sure if this is actually used?
- [x] buddy.endRelationship
- [x] buddy.accept
- [x] buddy.decline
- [x] buddy.search
- [x] buddy.invite
- [x] planes.upgrade
- [x] planes.buy
- [x] planes.scrap
- [x] resource_items.buy  -  Only QS for now
- [x] packages.buy
- [x] planes.createFlyBy
- [x] planes.send
- [x] planes.sendback
- [x] planes.sendbackflyby
- [x] planes.miss
- [x] planes.removeFlyByPlane
- [x] planes.takeMeans
- [x] planes.setState
- [x] planes.get
- [x] planes.onStartCargoTutorial  -  Doesn't seem necessary?
- [x] backgrounds.buy
- [x] backgrounds.makeCurrent
- [x] landmarks.buy
- [x] landmarks.makeCurrent
- [x] bays.buy
- [x] cargoshops.fillShop
- [x] cargoshops.collectSalesRevenue
- [x] cargoshops.buy
- [x] cargoshops.buyCapacity
- [x] cargoshops.buyCargo
- [x] runways.buy
- [x] terminals.buy
- [x] map_extensions.buy
- [x] hangars.buy
- [x] hangars.upgrade
- [ ] warehouses.buy
- [x] playerdata.setbooster
- [x] landside_buildings.buy
- [x] landside_buildings.harvest
- [x] goals.buyTask
- [x] souvenirs.takeReward - PARTIALLY (Missing Falcon)
- [x] special_buildings.buy
- [x] placeable.place  -  PARTIALLY
- [x] placeable.setInStorage  -  PARTIALLY
- [x] flashCookies.set
- [ ] backgrounds.sell
- [x] bays.sell
- [ ] landmarks.sell
- [x] landside_buildings.sell
- [x] runways.sell
- [x] terminals.sell
- [x] recycling.start
- [ ] recycling.instant
- [x] recycling.collect
- [x] crafting.processCraftingStep
- [x] crafting.buyMaterials
- [x] crafting.start
- [x] crafting.instant
- [x] crafting.collect
- [x] crafting.buySlot
- [x] general.trackFlashError
- [ ] materialevent.redeemItem

### Likely unused game commands
- account.getAll
- account.getData
- account.getRandom
- account.getDataByUserId
- buddy.getTutorialBuddy
- playerdata.getStats
- locations.get
- packets.get
- planes.changeFlightStatus
- planes.changeContainer
- backgrounds.get
- landmarks.get
- bays.get
- cargoshops.get
- runways.get
- terminals.get
- hangars.get
- warehouses.get
- landside_buildings.get
- souvenirs.buy
- expeditions.start
- expeditions.land
- expeditions.getanother
- expeditions.end
- expeditions.fillfuel
- expeditions.addfuel

### Not sure what those are
- catchits.get
- catchits.catchPrize
- planes.rebateMiss
- offers.buyOffer
