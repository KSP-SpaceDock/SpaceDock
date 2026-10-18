Chart = require('chart.js')

window.activateStats = ->
    return unless document.getElementById('downloads-over-time')?
    return unless window.versions?
    return unless window.download_stats?
    return unless window.downloads_per_version?
    return unless window.follower_stats?

    worker = new Worker('/static/statworker.js')

    worker.addEventListener 'message', (e) ->
        switch e.data.action

            when 'downloads_ready'
                canvas = document.getElementById('downloads-over-time')
                return unless canvas?

                new Chart(canvas,
                    type: 'line'
                    data:
                        labels: e.data.data.labels
                        datasets: e.data.data.entries
                    options:
                        legend:
                            fullWidth: true
                            position: 'bottom'
                            labels:
                                padding: 5
                                fontSize: 9
                                boxWidth: 12
                        scales:
                            yAxes: [
                                ticks:
                                    min: 0
                                    precision: 0
                            ]
                )

            when 'downloads_per_version_ready'
                canvas = document.getElementById('downloads-per-version')
                return unless canvas?

                new Chart(canvas,
                    type: 'bar'
                    data:
                        labels: e.data.data.labels
                        datasets: e.data.data.entries
                    options:
                        legend:
                            display: false
                        scales:
                            yAxes: [
                                ticks:
                                    min: 0
                                    precision: 0
                            ]
                )

            when 'followers_ready'
                canvas = document.getElementById('followers-over-time')
                return unless canvas?

                new Chart(canvas,
                    type: 'line'
                    data:
                        labels: e.data.data.labels
                        datasets: e.data.data.entries
                    options:
                        legend:
                            display: false
                        scales:
                            yAxes: [
                                ticks:
                                    suggestedMin: 0
                                    precision: 0
                            ]
                )

    , false

    worker.addEventListener 'error', (e) ->
        console.error('Stats worker failed:', e.message)
        worker.terminate()
    , false

    worker.postMessage(
        action: 'set_versions'
        data: window.versions
    )

    worker.postMessage(
        action: 'set_timespan'
        data: window.thirty_days_ago
    )

    worker.postMessage(
        action: 'process_downloads'
        data: window.download_stats
    )

    worker.postMessage(
        action: 'process_downloads_per_version'
        data: window.downloads_per_version
    )

    worker.postMessage(
        action: 'process_followers'
        data: window.follower_stats
    )
