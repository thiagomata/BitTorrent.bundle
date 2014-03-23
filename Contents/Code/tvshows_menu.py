################################################################################
SUBPREFIX = 'tvshows'

################################################################################
ALLOW_UNRECOGNIZED = False

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(popular, per_page=31), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search, per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', per_page=int, tvshow_count=int)
def popular(per_page, tvshow_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.tvshows_get_popular_torrents(torrent_infos)

    tvshow_infos = []
    tvshow_count = fill_tvshow_list(torrent_infos, tvshow_count, per_page, tvshow_infos)

    object_container = ObjectContainer(title2='Popular')
    parse_tvshow_infos(object_container, tvshow_infos)
    object_container.add(NextPageObject(key=Callback(popular, per_page=per_page, tvshow_count=tvshow_count), title="More..."))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query, per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.tvshows_search(query, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2='Popular')

    for torrent_info in torrent_infos:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(torrent_info.seeders, torrent_info.leechers)

        videoclip_object         = VideoClipObject()
        videoclip_object.title   = torrent_info.title
        videoclip_object.summary = seeders_leechers_line
        videoclip_object.url     = torrent_info.url

        object_container.add(videoclip_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow', tvshow_info=dict)
def tvshow(tvshow_info):
    object_container = ObjectContainer(title2=tvshow_info.title)
    return object_container

################################################################################
def fill_tvshow_list(torrent_infos, cur_tvshow_count, max_tvshow_count, tvshow_infos):
    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    tvshow_infos_keys      = set()
    tvshow_infos_skip_keys = set()

    for torrent_info in torrent_infos:
        tvshow_info = SharedCodeService.tvshows.TVShowInfo(torrent_info.title)

        if tvshow_info.tmdb_id or ALLOW_UNRECOGNIZED:
            if len(tvshow_infos_skip_keys) < cur_tvshow_count:
                tvshow_infos_skip_keys.add(tvshow_info.key)
            else:
                if not tvshow_info.key in tvshow_infos_skip_keys and not tvshow_info.key in tvshow_infos_keys:
                    tvshow_infos_keys.add(tvshow_info.key)
                    tvshow_infos.append(tvshow_info)
                    if len(tvshow_infos) == max_tvshow_count:
                        break

    return len(tvshow_infos_skip_keys) + len(tvshow_infos_keys)

################################################################################
def parse_tvshow_infos(object_container, tvshow_infos):
    for tvshow_info in tvshow_infos:
        tvshow_object       = TVShowObject()
        tvshow_object.title = tvshow_info.title

        if tvshow_info.tmdb_id:
            SharedCodeService.tmdb.fill_tvshow_metadata_object(tvshow_info.tmdb_id, tvshow_object)

        tvshow_object.key        = Callback(tvshow, tvshow_info=tvshow_info.to_dict())
        tvshow_object.rating_key = tvshow_info.key
        object_container.add(tvshow_object)
