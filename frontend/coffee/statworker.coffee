importScripts("/static/underscore-min.js")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
versions = null
thirty_days_ago = null

backgroundColor = [
    'rgba(222,93,93,0.7)'
    'rgba(93,222,93,0.7)'
    'rgba(93,93,222,0.7)'
    'rgba(222,158,93,0.7)'
    'rgba(222,93,222,0.7)'
    'rgba(222,222,93,0.7)'
    'rgba(93,222,222,0.7)'
]
borderColor = [
    'rgba(179,74,74,1)'
    'rgba(74,177,74,1)'
    'rgba(74,74,177,1)'
    'rgba(177,126,74,1)'
    'rgba(177,74,177,1)'
    'rgba(177,177,74,1)'
    'rgba(74,177,177,1)'
]

self.addEventListener('message', (e) ->
    switch e.data.action
        when "set_versions" then versions = e.data.data
        when "set_timespan" then thirty_days_ago = e.data.data
        when "process_downloads" then processDownloads(e.data.data)
        when "process_downloads_per_version" then processDownloadsPerVersion(e.data.data)
        when "process_followers" then processFollowers(e.data.data)
, false)

processDownloads = (download_stats) ->
    labels = []
    entries = []
    key = []
    for i in [0..30]
        a = new Date(thirty_days_ago.getTime())
        a.setDate(a.getDate() + i)
        labels.push("#{months[a.getMonth()]} #{a.getDate()}")
    color = 0
    for v in versions.reverse()
        data = []
        for i in [0..30]
            a = new Date(thirty_days_ago.getTime())
            a.setDate(a.getDate() + i)
            events = _.filter(download_stats, (d) ->
                b = new Date(d.created)
                return a.getDate() == b.getDate() and a.getMonth() == b.getMonth() and d.version_id == v.id
            )
            downloads = 0
            if events?
                downloads = _.reduce(events, (m, e) ->
                    return m + e.downloads
                , 0)
            data.push(downloads)
        if _.some(data, (d) -> d != 0)
            entries.push(
                label: v.name
                data: data
                backgroundColor: backgroundColor[color % backgroundColor.length]
                borderColor: borderColor[color % borderColor.length]
            )
            key.push(
                name: v.names
            )
        ++color
    postMessage(
        action: "downloads_ready"
        data:
            key: key
            entries: entries
            labels: labels
    )

processDownloadsPerVersion = (downloads_per_version) ->
    postMessage(
        action: "downloads_per_version_ready"
        data:
            labels: downloads_per_version.map((v) -> v[1])
            entries: [
                data: downloads_per_version.map((v) -> v[2]),
                backgroundColor: downloads_per_version.map((v, i) ->
                    backgroundColor[i % backgroundColor.length])
                borderColor: downloads_per_version.map((v, i) ->
                    borderColor[i % borderColor.length])
            ]
    )

processFollowers = (follower_stats) ->
    labels = []
    entries = []
    for i in [0..30]
        a = new Date(thirty_days_ago.getTime())
        a.setDate(a.getDate() + i)
        labels.push("#{months[a.getMonth()]} #{a.getDate()}")
    data = []
    for i in [0..30]
        a = new Date(thirty_days_ago.getTime())
        a.setDate(a.getDate() + i)
        events = _.filter(follower_stats, (d) ->
            b = new Date(d.created)
            return a.getDate() == b.getDate() and a.getMonth() == b.getMonth()
        )
        delta = 0
        if events?
            delta = _.reduce(events, (m, e) ->
                return m + e.delta
            , 0)
        data.push(delta)
    if _.some(data, (d) -> d != 0)
        entries.push(
            data: data
            backgroundColor: backgroundColor
            borderColor: borderColor
        )
    entries.reverse()
    postMessage(
        action: "followers_ready"
        data:
            entries: entries
            labels: labels
    )
