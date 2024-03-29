window.upload_bg = (files, box) ->
    file = files[0]
    p = document.createElement('p')
    p.textContent = 'Uploading...'
    p.className = 'status'
    box.appendChild(p)
    box.querySelector('a').classList.add('hidden')
    progress = box.querySelector('.upload-progress')

    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/game/#{window.game_id}/update-bg")
    xhr.setRequestHeader('Accept', 'application/json')
    xhr.upload.onprogress = (e) ->
        if e.lengthComputable
            progress.style.width = (e.loaded / e.total) * 100 + '%'
    xhr.onload = (e) ->
        if xhr.status != 200
            p.textContent = 'Please upload JPG or PNG only.'
            setTimeout(() ->
                box.removeChild(p)
                box.querySelector('a').classList.remove('hidden')
            , 3000)
        else
            resp = JSON.parse(xhr.responseText)
            p.textContent = 'Done!'
            document.getElementById('header-well').style.backgroundImage =
              'url("' + resp.path + '?nocache=' + new Date().getTime() + '")'
            setTimeout(() ->
                box.removeChild(p)
                box.querySelector('a').classList.remove('hidden')
            , 3000)
    formdata = new FormData()
    formdata.append('image', file)
    xhr.send(formdata)
