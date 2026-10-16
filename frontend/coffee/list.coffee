
loading = false
valid = true

get = (name) ->
    element = document.getElementById(name)
    if element? then element.value.trim() else ''

error = (name) ->
    element = document.getElementById(name)
    element.parentElement.classList.add('has-error') if element?
    document.getElementById('error-alert').classList.remove('hidden')
    valid = false

showError = (message) ->
    alertElement = document.getElementById('error-alert')
    alertElement.textContent = message or 'An unexpected error occurred.'
    alertElement.classList.remove('hidden')

resetForm = ->
    loading = false

    submit = document.getElementById('submit')
    submit.removeAttribute('disabled') if submit?

    progress = document.getElementById('progress')

    if progress?
        progress.classList.remove('active')
        bar = progress.querySelector('.progress-bar')
        bar.style.width = '0%' if bar?

    uploadLink = document.querySelector('.upload-mod a')
    uploadText = document.querySelector('.upload-mod p')

    uploadLink.classList.remove('hidden') if uploadLink?
    uploadText.classList.add('hidden') if uploadText?

submitButton = document.getElementById('submit')

if submitButton?
    submitButton.addEventListener('click', (e) ->
        e.preventDefault()

        return if loading

        document.querySelectorAll('.has-error').forEach (element) ->
            element.classList.remove('has-error')

        alertElement = document.getElementById('error-alert')
        alertElement.classList.add('hidden')
        valid = true

        name = get('pack-name')
        game = get('pack-game')

        error('pack-name') if name == ''
        error('pack-game') if game == ''

        return unless valid

        loading = true

        progress = document.getElementById('progress')
        bar = progress.querySelector('.progress-bar')
        bar.style.width = '0%'
        progress.classList.add('active')

        submitButton.setAttribute('disabled', 'disabled')

        xhr = new XMLHttpRequest()
        xhr.open('POST', '/api/pack/create')
        xhr.setRequestHeader('Accept', 'application/json')

        xhr.upload.onprogress = (e) ->
            if e.lengthComputable
                value = (e.loaded / e.total) * 100
                bar.style.width = value + '%'

        xhr.onload = ->
            result = null

            try
                result = JSON.parse(xhr.responseText)
            catch parseError
                showError('The server returned an invalid response.')
                resetForm()
                return

            if xhr.status < 200 or xhr.status >= 300
                showError(result.message or result.reason or 'Failed to create the mod pack.')
                resetForm()
                return

            if result.error?
                showError(result.message or result.reason or 'Failed to create the mod pack.')
                resetForm()
                return

            if result.url?
                window.location.href = result.url
            else
                showError('The server did not return a redirect URL.')
                resetForm()

        xhr.onerror = ->
            showError('Network error. Please check your connection and try again.')
            resetForm()

        xhr.onabort = ->
            showError('The request was cancelled.')
            resetForm()

        form = new FormData()
        form.append('name', name)
        form.append('game', game)

        xhr.send(form)
    , false)

    submitButton.removeAttribute('disabled')
