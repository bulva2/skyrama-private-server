# Skyrama Private Server

Skyrama Private Server is an attempt to create a custom server for Skyrama, a Bigpoint game. Not all features have been implemented, and those that are likely contain bugs. All help is welcome!

Keep in mind that although passwords should be properly encrypted/hashed, it is recommended to not use a password you use for any other services.

## Legal Notice / DMCA

This repository is made for educational and archival purposes only and will not be monetized in any way. We are NOT affiliated nor sponsored by Bigpoint GmbH. All game content, imagery, and trademarks are the property of Bigpoint GmbH. This project is not meant to replace Skyrama in any way. Please contact us for any legal problems, and we'll quickly take appropriate action. You can contact the repository owner on this Discord server: https://discord.gg/uFhJRvggZy.

## How to play

You will either need a browser that supports Flash (and Flash Player itself). We do NOT have own launcher so we cannot vouch fully for any available options but we have a good experience with:

- **[Recommended!] Older Ungoogled Chromium with Clean Flash:**
[Latest Ungoogled Chromium 87](https://github.com/tangalbert919/ungoogled-chromium-binaries/releases/download/87.0.4280.141-1/ungoogled-chromium_87.0.4280.141-1.1_installer-x64.exe)
&
[Clean Flash](https://cdn.cleanflash.org/CleanFlash_34.0.0.330_Installer.exe)<br>(Huge ♥️ to Darktohka for this project)

- **Standalone Flash Browser, no Flash Player required:**
[Flash Browser](https://github.com/radubirsan/FlashBrowser/releases/download/v0.81/v0.81_FlashBrowser_x64.exe)<br>
⚠️ May contain unmoderated ads, as the homepage is down, we recommend using the method above!

## Where can I try it out?

We currently host our own test server here: https://crimson-goat-16936.zap.cloud/
The server may be down anytime for maintenance or updates, use different login/password than you use in skyrama!

Also join us on [Discord](https://discord.gg/uFhJRvggZy)!

## How to run with Docker (recommended)

Everything (server + PostgreSQL + Caddy) comes up with one command. No database
to install, no credentials to invent.

1. Obtain the Skyrama `.swf` file, we cannot provide this on GitHub
2. Place it in the `assets` folder as `assets/airville.swf`
3. Run:

```bash
docker compose up -d --build
```

4. Open http://localhost and enjoy!

There is no `.env` to create for a local test — every setting has a working
default. Useful commands:

```bash
docker compose logs -f privaterama
```

To change anything (credentials, public address, TLS), copy `.env-example` to
`.env` and edit it:

- `DOMAIN` — see HTTPS below.
- `SESSION_SECRET` — **change this before exposing the server.** With the default
  value anyone can forge a logged-in session.
- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` — set once, used by both
  the database container and the server's connection string.
- `PUBLIC_URL` — only if you need to override the derived value, e.g. serving on
  a LAN IP like `http://192.168.1.50`. It is baked into the page as the Flash
  client's API host, so it must be the address players actually use.

Player data lives in the `pgdata` Docker volume and survives rebuilds.
`docker compose down -v` deletes it.

## HTTPS

Point your domain's A record at the server, put it in `.env`:

```
DOMAIN=skyrama.example.com
```

then `docker compose up -d`. That's the whole thing.

Caddy obtains the certificate on the first request, renews it in the background
forever, and redirects HTTP to HTTPS. `PUBLIC_URL` becomes
`https://skyrama.example.com` on its own, so there is nothing to keep in sync.

Certificates live in the `caddy_data` volume — don't delete it, or Caddy
re-requests them on restart and can hit Let's Encrypt rate limits.

## How to run the code locally (without Docker)

1. Obtain Skyrama .swf file, we cannot provide this on GitHub
2. Place Skyrama .swf file into assets folder
3. Install PostgreSQL and create a database
4. Rename .env-example to .env and set `DB_CONNECTION_STRING` to your database
5. Adjust host/port in config.cfg if needed
6. Run setup_database.py
7. Run scripts\setup.bat (.sh)
8. Run scripts\start.bat (.sh)
9. Enjoy!

## Known issues
- Some daily quests don't work

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
- [x] StoreLandsideBuilding
- [x] StoreTerminal

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
- [x] playerdata.getStats -> Stubbed for our purposes
- [x] playerdata.setLocation
- [x] playerdata.updateLevel
- [x] playerdata.updateSettings
- [x] evoucher.book
- [x] lucky_luggage.spin
- [x] buddy.getAll
- [x] buddy.collectPassenger
- [x] buddy.receivePassengers
- [x] buddy.endRelationship
- [x] buddy.accept
- [x] buddy.decline
- [x] buddy.search
- [x] buddy.invite
- [x] planes.upgrade
- [x] planes.buy
- [x] planes.scrap
- [x] resource_items.buy
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
- [x] planes.onStartCargoTutorial
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
- [x] playerdata.setbooster
- [x] landside_buildings.buy
- [x] landside_buildings.get
- [x] landside_buildings.harvest
- [x] goals.buyTask
- [x] souvenirs.takeReward -> PARTIALLY (Missing Falcon)
- [x] special_buildings.buy
- [x] placeable.place
- [x] placeable.setInStorage
- [x] flashCookies.set
- [ ] backgrounds.sell
- [x] bays.sell
- [ ] landmarks.sell
- [x] landside_buildings.sell
- [x] runways.sell
- [x] terminals.sell
- [x] recycling.start
- [x] recycling.instant
- [x] recycling.collect
- [x] crafting.processCraftingStep
- [x] crafting.buyMaterials
- [x] crafting.start
- [x] crafting.instant
- [x] crafting.collect
- [x] crafting.buySlot
- [x] general.trackFlashError
- [ ] materialevent.redeemItem
- [ ] offers.buyOffer -> Probably just stub this one

### Likely unused game commands
- account.getAll
- account.getData
- account.getRandom
- account.getDataByUserId
- buddy.getTutorialBuddy
- catchits.catchPrize
- catchits.get
- planes.rebateMiss
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
- souvenirs.buy
- expeditions.start
- expeditions.land
- expeditions.getanother
- expeditions.end
- expeditions.fillfuel
- expeditions.addfuel

### Unsure when is this used
- warehouses.buy -> (What is a warehouse??)
- warehouses.get -> (What is a warehouse??)
