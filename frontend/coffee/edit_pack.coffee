
editor = new Editor()
editor.render()

# Upload pack background image
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

    finish = ->
        setTimeout ->
            p.parentElement.removeChild(p) if p.parentElement?
            link.classList.remove('hidden')
            progress.style.width = '0%' if progress?
        , 3000

    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/pack/#{window.pack_id}/update-bg")
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.upload.onprogress = (e) ->
        if e.lengthComputable and progress?
            progress.style.width = (e.loaded / e.total * 100) + '%'

    xhr.onload = ->
        try
            resp = JSON.parse(xhr.responseText)

            if xhr.status < 200 or xhr.status >= 300
                throw new Error(resp.reason or resp.error or 'Please upload a valid JPG or PNG image.')

            if resp.error
                throw new Error(resp.reason or 'Upload failed.')

            unless resp.path?
                throw new Error('The server did not return an image path.')

            p.textContent = 'Done!'

            document.getElementById('header-well').style.backgroundImage =
                'url("' + resp.path + '?nocache=' + new Date().getTime() + '")'

        catch err
            p.textContent = err.message or 'Image upload failed.'

        finish()

    xhr.onerror = ->
        p.textContent = 'Network error while uploading the image.'
        finish()

    formdata = new FormData()
    formdata.append('image', file)
    xhr.send(formdata)


# Pack data
pack_list = (window.pack_list or []).map((id) -> parseInt(id, 10))
new_mod = null


# Enable or disable the add button
enableDisableAddModButton = ->
    btn = $("#add-mod-button")

    if new_mod == null
        btn.attr('title', 'Choose a mod in the dropdown to add')
        btn.prop('disabled', true)
    else
        btn.attr('title', '')
        btn.prop('disabled', false)


enableDisableAddModButton()


# Escape HTML text
escape_html = (str) ->
    return new Option(str).innerHTML


# Mod autocomplete
engine = new Bloodhound(
    name: 'mods'
    remote:
        url: "/api/typeahead/mod?game_id=#{window.game_id}&query=%QUERY"
        wildcard: '%QUERY'
    datumTokenizer: (d) ->
        Bloodhound.tokenizers.whitespace(d.name)
    queryTokenizer: Bloodhound.tokenizers.whitespace
)

engine.initialize().done ->
    $("#mod-typeahead").typeahead(
        highlight: true
    ,
        display: (mod) -> mod.name
        source: engine.ttAdapter()
    ).on('typeahead:selected typeahead:autocompleted', (e, mod) ->
        new_mod = mod
        enableDisableAddModButton()
    )


# Create a pack item
createPackItem = (mod) ->
    container = document.createElement('div')
    container.className = 'pack-item'
    container.dataset.mod = mod.id

    if mod.background?
        if mod.background != ''
            container.style.backgroundImage = "url('" + mod.background + "')"
        else
            container.style.backgroundImage = "url('/static/background-s.png')"
    else
        container.style.backgroundImage = "url('/static/background-s.png')"

    container.style.backgroundPosition = '0 ' + (mod.bg_offset_y or 0) + 'px'

    default_version = null

    if mod.versions?
        default_version = mod.versions.find((v) ->
            String(v.id) == String(mod.default_version_id)
        )

    version_text = ''
    game_version_text = ''

    if default_version?
        version_text = default_version.friendly_version or ''
        game_version_text = default_version.game_version or ''

    # Use DOM APIs and textContent for user-provided text
    well = document.createElement('div')
    well.className = 'well well-sm'

    controls = document.createElement('div')
    controls.className = 'pull-right'

    remove_button = document.createElement('button')
    remove_button.className = 'close remove'
    remove_button.type = 'button'
    remove_button.dataset.mod = mod.id
    remove_button.title = 'Remove mod'
    remove_button.innerHTML = '<span class="glyphicon glyphicon-trash"></span>'

    down_button = document.createElement('button')
    down_button.className = 'close down'
    down_button.type = 'button'
    down_button.dataset.mod = mod.id
    down_button.title = 'Move down'
    down_button.innerHTML = '<span class="glyphicon glyphicon-chevron-down"></span>'

    up_button = document.createElement('button')
    up_button.className = 'close up'
    up_button.type = 'button'
    up_button.dataset.mod = mod.id
    up_button.title = 'Move up'
    up_button.innerHTML = '<span class="glyphicon glyphicon-chevron-up"></span>'

    controls.appendChild(remove_button)
    controls.appendChild(down_button)
    controls.appendChild(up_button)

    heading = document.createElement('h3')
    mod_link = document.createElement('a')
    mod_link.href = mod.url or '#'
    mod_link.textContent = mod.name or 'Unnamed mod'

    heading.appendChild(mod_link)
    heading.appendChild(document.createTextNode(' ' + version_text + ' '))

    badge = document.createElement('span')
    badge.className = 'badge'
    badge.textContent = (mod.game or '') + ' ' + game_version_text
    heading.appendChild(badge)

    description = document.createElement('p')
    description.textContent = mod.short_description or ''

    well.appendChild(controls)
    well.appendChild(heading)
    well.appendChild(description)
    container.appendChild(well)

    remove_button.addEventListener('click', remove_mod, false)
    up_button.addEventListener('click', move_up, false)
    down_button.addEventListener('click', move_down, false)

    return container


# Keep the hidden form field synchronized
syncPackList = ->
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)
    window.pack_list = pack_list


# Add a mod
document.getElementById('add-mod-button').addEventListener('click', (e) ->
    e.preventDefault()

    if new_mod == null
        alert('Choose a mod in the dropdown to add')
        return

    mod_id = parseInt(new_mod.id, 10)

    if mod_id in pack_list
        alert('Already in list!')
        $("#mod-typeahead").typeahead('val', '')
        new_mod = null
        enableDisableAddModButton()
        return

    pack_list.push(mod_id)

    container = createPackItem(new_mod)
    document.getElementById('mods-list-box').appendChild(container)

    syncPackList()

    $("#mod-typeahead").typeahead('val', '')
    new_mod = null
    enableDisableAddModButton()

, false)


# Move item up
move_up = (e) ->
    e.preventDefault()

    mod_id = parseInt(e.currentTarget.dataset.mod, 10)
    move_where(mod_id, -1)


# Move item down
move_down = (e) ->
    e.preventDefault()

    mod_id = parseInt(e.currentTarget.dataset.mod, 10)
    move_where(mod_id, 1)


# Move item and update order
move_where = (mod_id, delta) ->
    i = pack_list.indexOf(mod_id)

    return if i < 0
    return if i + delta < 0 or i + delta >= pack_list.length

    array_swap(pack_list, i, i + delta)

    set_ordering(
        document.getElementById('mods-list-box'),
        pack_list
    )

    syncPackList()


# Swap two array elements
array_swap = (array, a, b) ->
    return array if a < 0 or b < 0
    return array if a >= array.length or b >= array.length

    tmp = array[a]
    array[a] = array[b]
    array[b] = tmp

    return array


# Reorder rendered pack items
set_ordering = (parent, array) ->
    elements = array.map((mod_id) ->
        parent.querySelector('.pack-item[data-mod="' + mod_id + '"]')
    )

    for element in elements
        if element?
            parent.appendChild(element)


# Remove a mod from the pack
remove_mod = (e) ->
    e.preventDefault()

    mod_id = parseInt(e.currentTarget.dataset.mod, 10)
    index = pack_list.indexOf(mod_id)

    return if index < 0

    element = document.querySelector(
        '.pack-item[data-mod="' + mod_id + '"]'
    )

    element.parentElement.removeChild(element) if element?.parentElement?

    pack_list.splice(index, 1)
    syncPackList()


# Attach handlers to existing items
for button in document.querySelectorAll('.pack-item .remove')
    button.addEventListener('click', remove_mod, false)

for button in document.querySelectorAll('.pack-item .up')
    button.addEventListener('click', move_up, false)

for button in document.querySelectorAll('.pack-item .down')
    button.addEventListener('click', move_down, false)
