window.activateStats = () ->
    worker = new Worker("/static/statworker.js")
    worker.addEventListener('message', (e) ->
        switch e.data.action
            when "downloads_ready"
                new Chart(document.getElementById('downloads-over-time').getContext("2d")).Line({
                    labels : e.data.data.labels,
                    datasets : e.data.data.entries
                },
                {
                    animation: false
                })
                keyUI = document.getElementById('downloads-over-time-key')
                for k in e.data.data.key
                    li = document.createElement('li')
                    keyColor = document.createElement('span')
                    keyText = document.createElement('span')
                    keyColor.className = 'key-color'
                    keyText.className = 'key-text'
                    keyColor.style.backgroundColor = k.color
                    keyText.textContent = k.name
                    li.appendChild(keyColor)
                    li.appendChild(keyText)
                    keyUI.appendChild(li)
            when "followers_ready"
                new Chart(document.getElementById('followers-over-time').getContext("2d")).Line({
                    labels : e.data.data.labels,
                    datasets : e.data.data.entries
                },
                {
                    animation: false
                })
    , false)
    worker.postMessage({ action: "set_versions", data: window.versions })
    worker.postMessage({ action: "set_timespan", data: window.thirty_days_ago })
    worker.postMessage({ action: "process_downloads", data: window.download_stats })
    worker.postMessage({ action: "process_followers", data: window.follower_stats })
