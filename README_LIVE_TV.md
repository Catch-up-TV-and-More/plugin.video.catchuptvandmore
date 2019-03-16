# How-to bind Catch-Up TV & More Live TV channels to Kodi Live TV feature


## Not tested with Kodi 17 (Krypton)!! Please use Leia!


1. Install Catch-Up TV & More and setup the needed Live TV accounts in the addon setting
2. Go in "Add-ons" tab on choose "Install from repository"
3. Choose "PVR clients"
4. Choose "PVR IPTV Simple Client"
5. Choose Install
6. Choose "PVR IPTV Simple Client"
7. Choose "Configure"
8. Go in "General" tab
9. Choose "Local Path" in "Location"
10. Choose "M3U Play List Path"
11. You have to go in your `special://home` folder (the path depend on your OS, check here: [Default OS mappings](https://kodi.wiki/view/Special_protocol#Default_OS_mappings)) then navigate in `addons/plugin.video.catchuptvandmore/resources` then choose the file `channels.m3u`
12. Go in "EPG Settings tab"
13. Choose "Remote Path" in "Location"
14. Copy `https://github.com/Catch-up-TV-and-More/xmltv/blob/master/tv_guide_fr.xml?raw=true` in "XMLTV URL"
15. Enable "Cache XMLTV at local storage"
12. Finally choose "Ok" in order to save the settings
13. Restart Kodi
14. Normally you can now found Live TV channels in the "TV" tabs of Kodi  


## Hide channels or country

If you don't want to have in your list a specific channel or all channels of a country you can hide channels and/or groups from `Kodi settings --> PVR & Live TV --> General --> Channel/group manager`.


