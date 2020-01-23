importScripts("/static/underscore.min.js")
months = ['Janurary', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
colors = [
    ['rgba(222,93,93,0.7)', 'rgba(179,74,74,1)'],
    ['rgba(93,222,93,0.7)', 'rgba(74,177,74,1)'],
    ['rgba(93,93,222,0.7)', 'rgba(74,74,177,1)'],
    ['rgba(222,158,93,0.7)', 'rgba(177,126,74,1)'],
    ['rgba(222,93,222,0.7)', 'rgba(177,74,177,1)'],
    ['rgba(222,222,93,0.7)', 'rgba(177,177,74,1)'],
    ['rgba(93,222,222,0.7)', 'rgba(74,177,177,1)']
]
versions = null
thirty_days_ago = null

self.addEventListener('message', (e) ->
    switch e.data.action
        when "set_versions" then versions = e.data.data
        when "set_timespan" then thirty_days_ago = e.data.data
        when "process_downloads" then processDownloads(e.data.data)
        when "process_followers" then processFollowers(e.data.data)
, false)

processDownloads = (download_stats) ->
    labels = []
    entries = []
    color = 0
    key = []
    for i in [0..30]
        a = new Date(thirty_days_ago.getTime())
        a.setDate(a.getDate() + i)
        labels.push("#{months[a.getMonth()]} #{a.getDate()}")
    for v in versions
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
            entries.push({
                fillColor: colors[color][0],
                pointColor: colors[color][1],
                pointStrokeColor: '#fff',
                pointHighlightFill: colors[color][0],
                pointHighlightStroke: '#fff',
                data: data
            })
            key.push({ name: v.name, color: colors[color][0] })
            color++
            if color >= colors.length
                color = 0
    entries.reverse()
    key.reverse()
    postMessage({
        action: "downloads_ready",
        data: {
            key: key,
            entries: entries,
            labels: labels
        }
    })

processFollowers = (follower_stats) ->
    labels = []
    entries = []
    color = 0
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
        entries.push({
            fillColor: colors[color][0],
            strokeColor: colors[color][1],
            pointColor: colors[color][1],
            pointStrokeColor: '#fff',
            data: data
        })
        color++
        if color >= colors.length
            color = 0
    entries.reverse()
    postMessage({
        action: "followers_ready",
        data: {
            entries: entries,
            labels: labels
        }
    })
