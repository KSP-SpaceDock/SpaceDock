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

    url = select.attr('data-url')

    unless url?
        console.error('Missing category endpoint URL.')
        return

    url = url.replace('__GAME_ID__', encodeURIComponent(gameid))

    $.ajax(
        method: 'GET'
        url: url
        dataType: 'json'

        success: (msg) ->
            select.empty()

            $.each msg, (el, category) ->
                return unless category.enabled

                option = $('<option></option>')
                    .val(category.id)
                    .text(category.name)

                if String(category.id) == String(window.mod_category_id)
                    option.prop('selected', true)

                select.append(option)

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

    unless link?
        p.textContent = 'Upload link not found.'
        return

    link.classList.add('hidden')

    if progress?
        progress.style.width = '0%'

    url = box.dataset.url

    unless url?
        p.textContent = 'Missing background upload URL.'
        link.classList.remove('hidden')
        return

    xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.upload.onprogress = (e) ->
        if e.lengthComputable and progress?
            progress.style.width = (e.loaded / e.total * 100) + '%'

    finish = ->
        setTimeout ->
            p.remove() if p.parentElement?
            link.classList.remove('hidden')

            if progress?
                progress.style.width = '0%'
        , 3000

    xhr.onload = ->
        try
            resp = JSON.parse(xhr.responseText)

            if xhr.status < 200 or xhr.status >= 300
                throw new Error(resp.reason or resp.error or 'Upload failed.')

            unless resp.path?
                throw new Error('The server did not return an image path.')

            p.textContent = 'Done!'

            header = document.getElementById('header-well')

            if header?
                header.style.backgroundImage =
                    'url("' + resp.path + '?nocache=' + new Date().getTime() + '")'

        catch err
            p.textContent = err.message or 'Please upload a valid JPG or PNG image.'

        finish()

    xhr.onerror = ->
        p.textContent = 'Network error while uploading the image.'
        finish()

    formdata = new FormData()
    formdata.append('image', file)
    xhr.send(formdata)


# Add a shared author
addAuthorButton = document.getElementById('add-shared-author')

if addAuthorButton?
    addAuthorButton.addEventListener 'click', (e) ->
        e.preventDefault()

        m = document.getElementById('shared-author-error')
        u = document.getElementById('new-shared-author')

        return unless m? and u?

        username = u.value.trim()
        m.classList.add('hidden