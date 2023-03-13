editor = new Editor()
editor.render()

window.upload_bg = (files, box) ->
    file = files[0]
    p = document.createElement('p')
    p.textContent = 'Uploading...'
    p.className = 'status'
    box.appendChild(p)
    box.querySelector('a').classList.add('hidden')
    progress = box.querySelector('.upload-progress')

    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/pack/#{window.pack_id}/update-bg")
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
            if resp.error
                alert resp.reason
            else
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

pack_list = window.pack_list
new_mod = null

enableDisableAddModButton = ->
    btn = $("#add-mod-button")
    if new_mod == null
        btn.attr('title', "Choose a mod in the dropdown to add")
        btn.prop('disabled', true)
    else
        btn.attr('title', "")
        btn.prop('disabled', false)

enableDisableAddModButton()

# https://stackoverflow.com/a/22706073
escape_html = (str) ->
    return new Option(str).innerHTML

engine = new Bloodhound({
    name: 'mods',
    remote: "/api/typeahead/mod?game_id=#{window.game_id}&query=%QUERY",
    datumTokenizer: (d) -> Bloodhound.tokenizers.whitespace(d.name),
    queryTokenizer: Bloodhound.tokenizers.whitespace
})
engine.initialize()
    .done( ->
        $("#mod-typeahead").typeahead({
            highlight: true,
        }, {
            displayKey: (mod) -> escape_html(mod.name),
            source: engine.ttAdapter()
        }).on("typeahead:selected typeahead:autocompleted", (e, m) ->
            new_mod = m
            enableDisableAddModButton()
        )
    )

document.getElementById('add-mod-button').addEventListener('click', (e) ->
    e.preventDefault()
    if new_mod == null
        alert("Choose a mod in the dropdown to add")
        return
    if new_mod.id in pack_list
        alert("Already in list!")
        $("#mod-typeahead").val('')
        new_mod = null
        enableDisableAddModButton()
        return
    pack_list.push(new_mod.id)
    container = document.createElement('div')
    container.className = 'pack-item'
    if new_mod.background != "" and new_mod.background != null
        container.style.backgroundImage = "url('" + new_mod.background + "')"
    else
        container.style.backgroundImage = "url('/static/background-s.png')"
    container.style.backgroundPosition = '0 ' + new_mod.bg_offset_y + 'px'
    container.dataset.mod = new_mod.id
    default_version = new_mod.versions.find((v) -> v.id == new_mod.default_version_id)
    container.innerHTML = """
    <div class="well well-sm">
        <div class="pull-right">
            <button class="close remove" data-mod="#{ new_mod.id }"><span class="glyphicon glyphicon-trash"></span></button>
            <button class="close down" data-mod="#{ new_mod.id }"><span class="glyphicon glyphicon-chevron-down"></span></button>
            <button class="close up" data-mod="#{ new_mod.id }"><span class="glyphicon glyphicon-chevron-up"></span></button>
        </div>
        <h3>
            <a href="#{new_mod.url}">#{new_mod.name}</a> #{default_version.friendly_version}
            <span class="badge">#{new_mod.game} #{default_version.game_version}</span>
        </h3>
        <p>#{new_mod.short_description}</p>
    </div>
    """
    container.querySelector('button.remove').addEventListener('click', remove_mod)
    container.querySelector('button.up').addEventListener('click', move_up)
    container.querySelector('button.down').addEventListener('click', move_down)
    document.getElementById('mods-list-box').appendChild(container)
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)
    $("#mod-typeahead").val('')
    new_mod = null
    enableDisableAddModButton()
)

move_up = (e) ->
    e.preventDefault()
    mod_id = parseInt(e.currentTarget.dataset.mod, 10)
    move_where(mod_id, -1)

move_down = (e) ->
    e.preventDefault()
    mod_id = parseInt(e.currentTarget.dataset.mod, 10)
    move_where(mod_id, 1)

move_where = (mod_id, delta) ->
    i = pack_list.indexOf(mod_id)
    set_ordering(document.getElementById('mods-list-box'),
        array_swap(pack_list, i, i + delta))
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)

array_swap = (array, a, b) ->
    a = (a + array.length) % array.length
    b = (b + array.length) % array.length
    tmp = array[a]
    array[a] = array[b]
    array[b] = tmp
    return array

set_ordering = (parent, array) ->
    elements = array.map((mod_id) -> document.querySelector('.pack-item[data-mod="' + mod_id + '"]'))
    while parent.children.length > 0
        parent.removeChild(parent.lastChild)
    for elt in elements
        parent.appendChild(elt)

remove_mod = (e) ->
    e.preventDefault()
    mod_id = e.currentTarget.dataset.mod
    d = document.querySelector('.pack-item[data-mod="' + mod_id + '"]')
    d.parentElement.removeChild(d)
    pack_list.splice(pack_list.indexOf(parseInt(mod_id, 10)), 1)
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)

c.addEventListener('click', remove_mod) for c in document.querySelectorAll('.pack-item .remove')
c.addEventListener('click', move_up) for c in document.querySelectorAll('.pack-item .up')
c.addEventListener('click', move_down) for c in document.querySelectorAll('.pack-item .down')
