Chart = require('chart.js')

window.activateStats = () ->
    worker = new Worker("/static/statworker.js")
    worker.addEventListener('message', (e) ->
        switch e.data.action

            when "downloads_ready"
                new Chart(document.getElementById('downloads-over-time'),
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

            when "downloads_per_version_ready"
                new Chart(document.getElementById('downloads-per-version'),
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

            when "followers_ready"
                new Chart(document.getElementById('followers-over-time'),
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

    , false)
    worker.postMessage(
        action: "set_versions"
        data: window.versions
    )
    worker.postMessage(
        action: "set_timespan"
        data: window.thirty_days_ago
    )
    worker.postMessage(
        action: "process_downloads"
        data: window.download_stats
    )
    worker.postMessage(
        action: "process_downloads_per_version"
        data: window.downloads_per_version
    )
    worker.postMessage(
        action: "process_followers"
        data: window.follower_stats
    )
