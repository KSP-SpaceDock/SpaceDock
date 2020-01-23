loading = false
valid = true
get = (name) -> document.getElementById(name).value
error = (name) ->
    document.getElementById(name).parentElement.classList.add('has-error')
    document.getElementById('error-alert').classList.remove('hidden')
    valid = false



document.getElementById('submit').addEventListener('click', () ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')
    document.getElementById('error-alert').classList.add('hidden')
    valid = true

    name = get('pack-name')

    error('pack-name') if name == ''

    game = get('pack-game')

    error('pack-game') if game == ''

    return unless valid
    return if loading
    loading = true

    progress = document.getElementById('progress')
    xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/pack/create')
    xhr.upload.onprogress = (e) ->
        if e.lengthComputable
            value = (e.loaded / e.total) * 100
            progress.querySelector('.progress-bar').style.width = value + '%'
    xhr.onload = () ->
        result = JSON.parse(this.responseText)
        progress.classList.remove('active')
        if not result.error?
            window.location = JSON.parse(this.responseText).url
        else
            alert = document.getElementById('error-alert')
            alert.classList.remove('hidden')
            alert.textContent = result.message
            document.getElementById('submit').removeAttribute('disabled')
            document.querySelector('.upload-mod a').classList.remove('hidden')
            document.querySelector('.upload-mod p').classList.add('hidden')
            loading = false
    form = new FormData()
    form.append('name', name)
    form.append('game', game)
    document.getElementById('submit').setAttribute('disabled', 'disabled')
    progress.querySelector('.progress-bar').style.width = '0%'
    progress.classList.add('active')
    xhr.send(form)
, false)

document.getElementById('submit').removeAttribute('disabled')
