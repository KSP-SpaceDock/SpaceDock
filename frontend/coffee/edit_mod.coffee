
editor = new Editor()
editor.render()

# Update the displayed category name
updateCategoryNames = ->
    categoryName = $('#mod-category option:selected').text().trim()
    $('.mod-category-name').text(categoryName)


# Load categories for the selected game
updatecategories = (gameid) ->
    select = $('#mod-category')
    select.empty()

    return unless gameid?

    select.append(
        $('<option></option>')
            .val('')
            .text('Loading categories...')
            .prop('disabled', true)
            .prop('selected', true)
    )

    select.trigger('chosen:updated')

    $.ajax(
        method: 'GET'
        url: '/api/' + gameid + '/categories'
        dataType: 'json'

        success: (msg) ->
            select.empty()

            $.each(msg, (el, category) ->
                return unless category.enabled

                option = $('<option></option>')
                    .val(category.id)
                    .text(category.name)

                if String(category.id) == String(window.mod_category_id)
                    option.prop('selected', true)

                select.append(option)
            )

            if select.find('option').length == 0
                select.append(
                    $('<option></option>')
                        .val('')
                        .text('No categories available')
                        .prop('disabled', true)
                )

            select.trigger('chosen:updated')
            updateCategoryNames()

        error: (xhr) ->
            console.error('Failed to load categories:', xhr.status)

            select.empty()
            select.append(
                $('<option></option>')
                    .val('')
                    .text('Failed to load categories')
                    .prop('disabled', true)
            )

            select.trigger('chosen:updated')
            updateCategoryNames()
    )


# Initialize the category selector
$(document).ready ->
    $('#mod-category').chosen(
        max_selected_options: 1
        no_results_text: 'No Options found'
        width: '100%'
    )

    $('#mod-category').on 'change', updateCategoryNames

    updatecategories(window.game_id)


# Upload a mod background image
window.upload_bg = (files, box) ->
    return unless files? and files.length > 0

    file = files[0]
    p = document.createElement('p')
    p.textContent = 'Uploading...'
    p.className = 'status'
    box.appendChild(p)

    link = box.querySelector('a')
    progress = box.querySelector('.upload-progress')

    link.classList.add('hidden')

    if progress?
        progress.style.width = '0%'

    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/mod/#{window.mod_id}/update-bg")
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.upload.onprogress = (e) ->
        if e.lengthComputable and progress?
            progress.style.width = (e.loaded / e.total * 100) + '%'

    xhr.onload = ->
        try
            resp = JSON.parse(xhr.responseText)

            if xhr.status < 200 or xhr.status >= 300
                throw new Error(resp.reason or resp.error or 'Upload failed.')

            unless resp.path?
                throw new Error('The server did not return an image path.')

            p.textContent = 'Done!'

            document.getElementById('header-well').style.backgroundImage =
                'url("' + resp.path + '?nocache=' + new Date().getTime() + '")'

        catch err
            p.textContent = err.message or 'Please upload a valid JPG or PNG image.'

        setTimeout ->
            if p.parentElement?
                p.parentElement.removeChild(p)

            link.classList.remove('hidden')

            if progress?
                progress.style.width = '0%'
        , 3000

    xhr.onerror = ->
        p.textContent = 'Network error while uploading the image.'

        setTimeout ->
            if p.parentElement?
                p.parentElement.removeChild(p)

            link.classList.remove('hidden')
        , 3000

    formdata = new FormData()
    formdata.append('image', file)
    xhr.send(formdata)


# Add a shared author
document.getElementById('add-shared-author').addEventListener 'click', (e) ->
    e.preventDefault()

    m = document.getElementById('shared-author-error')
    u = document.getElementById('new-shared-author')
    username = u.value.trim()

    m.classList.add('hidden')

    if username == ''
        m.textContent = 'Please enter a username.'
        m.classList.remove('hidden')
        return

    xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/mod/' + window.mod_id + '/grant')
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.onload = ->
        try
            response = JSON.parse(xhr.responseText)

            if xhr.status < 200 or xhr.status >= 300 or response.error
                m.textContent = response.reason or response.error or 'Failed to add author.'
                m.classList.remove('hidden')
                return

            div = document.createElement('div')
            div.className = 'col-md-6'
            div.appendChild(document.createTextNode(username + ' (pending) '))

            a = document.createElement('a')
            a.href = '#'
            a.dataset.user = username
            a.className = 'remove-author'
            a.addEventListener('click', remove_coauthor, false)

            span = document.createElement('span')
            span.className = 'glyphicon glyphicon-remove'
            a.appendChild(span)

            div.appendChild(a)

            b = document.getElementById('beforeme')
            b.parentElement.insertBefore(div, b)

            u.value = ''

        catch err
            m.textContent = 'Invalid response from server.'
            m.classList.remove('hidden')

    xhr.onerror = ->
        m.textContent = 'Network error. Please try again.'
        m.classList.remove('hidden')

    data = new FormData()
    data.append('user', username)
    xhr.send(data)

, false


# Submit when Enter is pressed in the username field
document.getElementById('new-shared-author').addEventListener 'keypress', (e) ->
    if e.keyCode == 13
        e.preventDefault()
        document.getElementById('add-shared-author').click()

, false


# Remove a shared author
remove_coauthor = (e) ->
    e.preventDefault()

    target = e.currentTarget
    username = target.dataset.user

    return unless username?

    xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/mod/' + window.mod_id + '/revoke')
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.onload = ->
        if xhr.status >= 200 and xhr.status < 300
            window.location.reload()
        else
            console.error('Failed to remove author:', xhr.status)

    xhr.onerror = ->
        console.error('Network error while removing author.')

    form = new FormData()
    form.append('user', username)
    xhr.send(form)


# Attach removal handlers to existing shared authors
for a in document.querySelectorAll('.remove-author')
    a.addEventListener('click', remove_coauthor, false)
