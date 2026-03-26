var preview = $('.preview');
var label = $('.upload-card');
var inputFile = $('[type=file]');
var deleteButton = $('.delete-button');

$(document).ready(function() {
    inputFile.on('change', function() {
        const file = inputFile.get(0).files[0];
        if(file) {
    
            var  reader = new FileReader();
            reader.onload = function() {
                preview.attr('src', reader.result);
            }
            reader.readAsDataURL(file);
            label.addClass('shown');
            inputFile.prop('disabled', false);
        }
    });
    
    deleteButton.on('click', function() {
        preview.attr('src', '');
        label.removeClass('shown');
        inputFile.prop('disabled', false);
    });

});