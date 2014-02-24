################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='TV Shows')
	object_container.add(DirectoryObject(key=Callback(popular, title='Popular'), title='Popular', thumb=R(SharedCodeService.common.ICON)))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular')
def popular(title, page=1):
	popular_json_url  = 'http://api.themoviedb.org/3/tv/popular?page={0}&api_key=a3dc111e66105f6387e99393813ae4d5'.format(page)
	popular_json_data = JSON.ObjectFromURL(popular_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title2=title)

	for tvshow in popular_json_data['results']:
		object_container.add(create_tvshow_object(tvshow['id']))

	if page < popular_json_data['total_pages']:
		object_container.add(NextPageObject(key=Callback(popular, title=title, page=page + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, page=1):
	search_json_url  = 'http://api.themoviedb.org/3/search/tv?query={0}&api_key=a3dc111e66105f6387e99393813ae4d5'.format(String.Quote(query))
	search_json_data = JSON.ObjectFromURL(search_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title2=title)

	for tvshow in search_json_data['results']:
		object_container.add(create_tvshow_object(tvshow['id']))

	if page < search_json_data['total_pages']:
		object_container.add(NextPageObject(key=Callback(search, title=title, page=page + 1), title="More..."))

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
		tvshow_object.art = Callback(get_image_async, url= SharedCodeService.themoviedb.get_image_url(tvshow_json_data['backdrop_path']))
	except:
		pass

	try:
		tvshow_object.thumb = Callback(get_image_async, url=SharedCodeService.themoviedb.get_image_url(tvshow_json_data['poster_path']))
	except:
		pass

	tvshow_object.key        = Callback(show, title=tvshow_object.title, tmdb_id=tmdb_id)
	tvshow_object.rating_key = '{0}-{1}'.format(tmdb_id, tvshow_object.title.replace(' ', '-').lower())

	return tvshow_object

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/show')
def show(title, tmdb_id):
	show_json_url  = 'http://api.themoviedb.org/3/tv/{0}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id)
	show_json_data = JSON.ObjectFromURL(show_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title1=show_json_data['name'], title2=title)

	for show_season in show_json_data['seasons']:
		if not show_season['air_date'] or (Datetime.ParseDate(show_season['air_date']) - Datetime.Now()) > Datetime.Delta(days=0):
			continue

		if show_season['season_number'] == 0:
			continue

		season_json_url  = 'http://api.themoviedb.org/3/tv/{0}/season/{1}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id, show_season['season_number'])
		season_json_data = JSON.ObjectFromURL(season_json_url, cacheTime=CACHE_1DAY)

		season_object               = SeasonObject()
		season_object.show          = show_json_data['name']
		season_object.index         = season_json_data['season_number']
		season_object.title         = season_json_data['name']
		season_object.summary       = season_json_data['overview']
		season_object.episode_count = len(season_json_data['episodes'])
		season_object.key           = Callback(season, title=season_object.title, tmdb_id=tmdb_id, show=season_object.show, season_index=season_object.index)
		season_object.rating_key    = '{0}-{1}-{2}'.format(tmdb_id, season_object.show.replace(' ', '-').lower(), season_object.index)

		try:
			season_object.originally_available_at = Datetime.ParseDate(movie_data['air_date']).date()
			season_object.year                    = season_object.originally_available_at.year
		except:
			pass

		try:
			season_object.art = Callback(get_image_async, url=SharedCodeService.themoviedb.get_image_url(show_json_data['backdrop_path']))
		except:
			pass

		try:
			season_object.thumb = Callback(get_image_async, url=SharedCodeService.themoviedb.get_image_url(season_json_data['poster_path']))
		except:
			pass

		object_container.add(season_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season(title, tmdb_id, show, season_index):
	season_json_url  = 'http://api.themoviedb.org/3/tv/{0}/season/{1}?&api_key=a3dc111e66105f6387e99393813ae4d5'.format(tmdb_id, season_index)
	season_json_data = JSON.ObjectFromURL(season_json_url, cacheTime=CACHE_1DAY)

	object_container = ObjectContainer(title1=season_json_data['name'], title2=title)

	for episode in season_json_data['episodes']:
		if not episode['air_date'] or (Datetime.ParseDate(episode['air_date']) - Datetime.Now()) > Datetime.Delta(days=0):
			continue

		episode_object = SharedCodeService.themoviedb.create_episode_object(tmdb_id, show, season_index, episode['episode_number'])

		try:
			episode_object.art = Callback(get_image_async, url=episode_object.art)
		except:
			pass

		try:
			episode_object.thumb = Callback(get_image_async, url=episode_object.thumb)
		except:
			pass

		object_container.add(episode_object)

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/get_image_async')
def get_image_async(url):
	return Redirect(url)
