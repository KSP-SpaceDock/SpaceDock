
window.upload_bg = (files, box) ->
    return unless files? and files.length > 0

    file = files[0]

    p = document.createElement('p')
    p.textContent = 'Uploading...'
    p.className = 'status'
    box.appendChild(p)

    link = box.querySelector('a')
    link.classList.add('hidden') if link?

    progress = box.querySelector('.upload-progress')

    if progress?
        progress.style.width = '0%'

    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/game/#{window.game_id}/update-bg")
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.upload.onprogress = (e) ->
        if e.lengthComputable and progress?
            percent = (e.loaded / e.total) * 100
            progress.style.width = percent + '%'

    xhr.onload = ->
        response = null

        try
            response = JSON.parse(xhr.responseText)
        catch error
            response = null

        if xhr.status < 200 or xhr.status >= 300
            p.textContent =
                if response?.reason?
                    response.reason
                else if response?.error?
                    response.error
                else
                    'Upload failed. Please upload a JPG or PNG image.'

        else if not response?
            p.textContent = 'The server returned an invalid response.'

        else if response.error
            p.textContent = response.reason or 'Failed to update the background.'

        else
            p.textContent = 'Done!'

            header = document.getElementById('header-well')

            if header? and response.path?
                header.style.backgroundImage =
                    'url("' + response.path + '?nocache=' + new Date().getTime() + '")'

            if progress?
                progress.style.width = '100%'

        setTimeout ->
            box.removeChild(p) if p.parentElement is box
            link.classList.remove('hidden') if link?
            if progress?
                progress.style.width = '0%'
        , 3000

    xhr.onerror = ->
        p.textContent = 'Network error. Please try again.'

        setTimeout ->
            box.removeChild(p) if p.parentElement is box
            link.classList.remove('hidden') if link?
            if progress?
                progress.style.width = '0%'
        , 3000

    xhr.onabort = ->
        p.textContent = 'Upload cancelled.'

        setTimeout ->
            box.removeChild(p) if p.parentElement is box
            link.classList.remove('hidden') if link?
            if progress?
                progress.style.width = '0%'
        , 3000

    formdata = new FormData()
    formdata.append('image', file)

    xhr.send(formdata)
