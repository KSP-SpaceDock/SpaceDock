zipFile = null
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

    gameVersion = get('game-version')
    version = get('version')
    changelog = get('changelog')
    notifyFollowers = document.getElementById('notify-followers').checked

    error('version') if version == ''
    if zipFile == null
        valid = false

    return unless valid
    return if loading
    loading = true

    progress = document.getElementById('progress')
    xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/mod/' + window.mod_id + '/update')
    xhr.upload.onprogress = (e) ->
        if e.lengthComputable
            value = (e.loaded / e.total) * 100
            progress.querySelector('.progress-bar').style.width = value + '%'
    xhr.onload = () ->
        if this.statusCode == 502
            result = { error: true, message: "This mod is too big to upload. Contact {{ support_mail }}" }
        else
            result = JSON.parse(this.responseText)
        progress.classList.remove('active')
        if not result.error?
            window.location = JSON.parse(this.responseText).url
        else
            alert = document.getElementById('error-alert')
            alert.classList.remove('hidden')
            alert.textContent = result.reason
            document.getElementById('submit').removeAttribute('disabled')
            document.querySelector('.upload-mod a').classList.remove('hidden')
            document.querySelector('.upload-mod p').classList.add('hidden')
            loading = false
    form = new FormData()
    form.append('game-version', gameVersion)
    form.append('version', version)
    form.append('changelog', changelog)
    form.append('notify-followers', notifyFollowers)
    form.append('zipball', zipFile)
    document.getElementById('submit').setAttribute('disabled', 'disabled')
    progress.classList.add('active')
    progress.querySelector('.progress-bar').style.width = '0%'
    xhr.send(form)
, false)

selectFile = (file) ->
    zipFile = file
    parent = document.querySelector('.upload-mod')
    parent.querySelector('a').classList.add('hidden')
    p = document.createElement('p')
    p.textContent = 'Ready.'
    parent.appendChild(p)

document.querySelector('.upload-mod a').addEventListener('click', (e) ->
    e.preventDefault()
    document.querySelector('.upload-mod input').click()
, false)

document.querySelector('.upload-mod input').addEventListener('change', (e) ->
    selectFile(e.target.files[0])
, false)

dragNop = (e) ->
    e.stopPropagation()
    e.preventDefault()

window.addEventListener('dragenter', dragNop, false)
window.addEventListener('dragleave', dragNop, false)
window.addEventListener('dragover', dragNop, false)
window.addEventListener('drop', (e) ->
    dragNop(e)
    selectFile(e.dataTransfer.files[0])
, false)

document.getElementById('submit').removeAttribute('disabled')
