$('.modal-confirm-delete').on 'show.bs.modal', (evt) ->
    # Disable final Delete button on modal open
    $(evt.target).find('input[type=submit]').prop('disabled', true)
    # Clear username confirmation text box on modal open
    $(evt.target).find('input[type=text]').val('')

$('.modal-confirm-delete').on 'shown.bs.modal', (evt) ->
    # Focus text box on modal open
    $(evt.target).find('input[type=text]').focus()

$('.confirm-username').on 'input', (evt) ->
    # Enable/disable final Delete button on confirmation text box change
    $("#btn-delete-#{evt.target.dataset.userid}").prop('disabled',
        evt.target.value != evt.target.dataset.username)
