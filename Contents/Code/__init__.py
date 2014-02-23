################################################################################
import kickasstorrents_menu
import thepiratebay_menu
import yts_menu

################################################################################
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE)
def Main():
	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(tvshows, title='TV Shows'), title='TV Shows', thumb=R(ICON)))
	object_container.add(DirectoryObject(key=Callback(kickasstorrents_menu.menu), title='KickassTorrents', thumb=R('kickasstorrents.png')))
	object_container.add(DirectoryObject(key=Callback(thepiratebay_menu.menu), title='The Pirate Bay', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
	object_container.add(PrefsObject(title='Preferences'))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshows')
def tvshows(title):
	object_container = ObjectContainer(title2=title)
	object_container.add(DirectoryObject(key=Callback(tvshows_popular, title='Popular'), title='Popular', thumb=R(ICON)))
	object_container.add(InputDirectoryObject(key=Callback(tvshows_search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshows_popular')
def tvshows_popular(title, page=1):
	popular_json_url  = 'http://api.themoviedb.org/3/tv/popular?page={0}&api_key=a3dc111e66105f6387e99393813ae4d5'.format(page)
	popular_json_data = JSON.ObjectFromURL(popular_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title2=title)

	for tvshow in popular_json_data['results']:
		object_container.add(create_tvshow_object(tvshow['id']))

	if page < popular_json_data['total_pages']:
		object_container.add(NextPageObject(key=Callback(tvshows_popular, title=title, page=page + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshows_search')
def tvshows_search(title, query, page=1):
	search_json_url  = 'http://api.themoviedb.org/3/search/tv?query={0}&api_key=a3dc111e66105f6387e99393813ae4d5'.format(String.Quote(query))
	search_json_data = JSON.ObjectFromURL(search_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title2=title)

	for tvshow in search_json_data['results']:
		object_container.add(create_tvshow_object(tvshow['id']))

	if page < search_json_data['total_pages']:
		object_container.add(NextPageObject(key=Callback(tvshows_search, title=title, page=page + 1), title="More..."))

	return object_container

################################################################################
def create_tvshow_object(tmdb_id):
	tvshow_json_url  = 'http://api.themoviedb.org/3/tv/{0}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id)
	tvshow_json_data = JSON.ObjectFromURL(tvshow_json_url, cacheTime=CACHE_1DAY)

	tvshow_object               = TVShowObject()
	tvshow_object.title         = tvshow_json_data['name']
	tvshow_object.summary       = tvshow_json_data['overview']
	tvshow_object.episode_count = tvshow_json_data['number_of_episodes']
	
	for genre in tvshow_json_data['genres']:
		tvshow_object.genres.add(genre['name'])

	try:
		tvshow_object.originally_available_at = Datetime.ParseDate(movie_data['first_air_date']).date()
		tvshow_object.year                    = tvshow_object.originally_available_at.year
	except:
		pass

	try:
		tvshow_object.art = Callback(get_image_async, url=get_image_url(tvshow_json_data['backdrop_path']))
	except:
		pass

	try:
		tvshow_object.thumb = Callback(get_image_async, url=get_image_url(tvshow_json_data['poster_path']))
	except:
		pass

	tvshow_object.key        = Callback(tvshow, title=tvshow_object.title, tmdb_id=tmdb_id)
	tvshow_object.rating_key = '{0}-{1}'.format(tmdb_id, tvshow_object.title.replace(' ', '-').lower())

	return tvshow_object

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshow')
def tvshow(title, tmdb_id):
	tvshow_json_url  = 'http://api.themoviedb.org/3/tv/{0}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id)
	tvshow_json_data = JSON.ObjectFromURL(tvshow_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title1=tvshow_json_data['name'], title2=title)

	for season in tvshow_json_data['seasons']:
		if not season['air_date'] or (Datetime.ParseDate(season['air_date']) - Datetime.Now()) > Datetime.Delta(days=0):
			continue

		if season['season_number'] == 0:
			continue

		season_json_url  = 'http://api.themoviedb.org/3/tv/{0}/season/{1}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id, season['season_number'])
		season_json_data = JSON.ObjectFromURL(season_json_url, cacheTime=CACHE_1DAY)

		season_object               = SeasonObject()
		season_object.show          = tvshow_json_data['name']
		season_object.index         = season_json_data['season_number']
		season_object.title         = season_json_data['name']
		season_object.summary       = season_json_data['overview']
		season_object.episode_count = len(season_json_data['episodes'])
		season_object.key           = Callback(tvshow_season, title=season_object.title, tmdb_id=tmdb_id, show=season_object.show, season_index=season['season_number'])
		season_object.rating_key    = '{0}-{1}-{2}'.format(tmdb_id, season_object.show.replace(' ', '-').lower(), season_object.index)

		try:
			season_object.originally_available_at = Datetime.ParseDate(movie_data['air_date']).date()
			season_object.year                    = season_object.originally_available_at.year
		except:
			pass

		try:
			season_object.art = Callback(get_image_async, url=get_image_url(tvshow_json_data['backdrop_path']))
		except:
			pass

		try:
			season_object.thumb = Callback(get_image_async, url=get_image_url(season_json_data['poster_path']))
		except:
			pass

		object_container.add(season_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshow_season', season_index=int)
def tvshow_season(title, tmdb_id, show, season_index):
	season_json_url  = 'http://api.themoviedb.org/3/tv/{0}/season/{1}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id, season_index)
	season_json_data = JSON.ObjectFromURL(season_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title1=season_json_data['name'], title2=title)

	for episode in season_json_data['episodes']:
		if not episode['air_date'] or (Datetime.ParseDate(episode['air_date']) - Datetime.Now()) > Datetime.Delta(days=0):
			continue

		episode_object            = EpisodeObject()
		episode_object.show       = show
		episode_object.season     = season_index
		episode_object.index      = episode['episode_number']
		episode_object.title      = episode['name']
		episode_object.summary    = episode['overview']
		episode_object.key        = Callback(tvshow_episode)
		episode_object.rating_key = '{0}-{1}-{2}-{3}'.format(tmdb_id, show.replace(' ', '-').lower(), season_index, episode_object.index)

		try:
			episode_object.originally_available_at = Datetime.ParseDate(movie_data['air_date']).date()
			episode_object.year                    = episode_object.originally_available_at.year
		except:
			pass

		try:
			episode_object.art = Callback(get_image_async, url=get_image_url(episode['still_path']))
		except:
			pass

		try:
			episode_object.thumb = Callback(get_image_async, url=get_image_url(episode['still_path']))
		except:
			pass

		object_container.add(episode_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/tvshow_episode')
def tvshow_episode():
	pass

################################################################################
def get_image_url(field):
	return SharedCodeService.tmdb.get_config()['images']['base_url'] + 'original' + field

################################################################################
@route(SharedCodeService.common.PREFIX + '/get_image_async')
def get_image_async(url):
	return Redirect(url)

################################################################################
def tvshow_predb_data(title):
	PREDB_SEARCH = 'http://predb.me/?search=title%3A{0}+tags%3Aaired%2C-foreign%2C-multi-language%2C-complete+-hungarian&page={1}'

	title = title.replace(' ', '-').lower()

	html_url  = PREDB_SEARCH.format(title, 1)
	html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1DAY)

	for item in html_data.xpath('//*[@class="p-c p-c-title"]/h2/a/text()'):
		Log.Info('Found release: {0}'.format(item))

	try:
		page_count = int(html_data.xpath('//a[@class="page-button load-more"]/@data')[0])
	except:
		page_count = 1

	for i in range(2, page_count + 1):
		html_url  = PREDB_SEARCH.format(title, i)
		html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1DAY)

		for item in html_data.xpath('//*[@class="p-c p-c-title"]/h2/a/text()'):
			Log.Info('Found release: {0}'.format(item))
