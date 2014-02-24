################################################################################
import kickasstorrents_menu
import thepiratebay_menu
import tvshows_menu
import yts_menu

################################################################################
def Start():
	ObjectContainer.art    = R(SharedCodeService.common.ART)
	ObjectContainer.title1 = SharedCodeService.common.TITLE
	VideoClipObject.art    = R(SharedCodeService.common.ART)
	VideoClipObject.thumb  = R(SharedCodeService.common.ICON)

################################################################################
@handler(SharedCodeService.common.PREFIX, SharedCodeService.common.TITLE)
def Main():
	object_container = ObjectContainer(title2=SharedCodeService.common.TITLE)
	object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows', thumb=R(SharedCodeService.common.ICON)))
	object_container.add(DirectoryObject(key=Callback(kickasstorrents_menu.menu), title='KickassTorrents', thumb=R('kickasstorrents.png')))
	object_container.add(DirectoryObject(key=Callback(thepiratebay_menu.menu), title='The Pirate Bay', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
	object_container.add(PrefsObject(title='Preferences'))
	return object_container
