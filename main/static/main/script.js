$(document).ready( function() {
    /* Set header height properly */
    var window_height = $(window).innerHeight();
    var nav_height = $('#nav').innerHeight();
    $('#header').css('min-height', window_height-nav_height);

    /* Display the selected assignment files */
    $('#assignment-submit').change( function() {
        var files = $(this)[0].files; // All the selected files (from input field)

        var noFileChosenMsg = $('#noFileChosenMsg');
        $(noFileChosenMsg).css({'display': 'block'});

        // Clear the previous file widgets
        var prevFiles = $("#selectedFiles").find('div');
        for (let i=0; i < prevFiles.length; i++) {
            $(prevFiles[i]).remove();
        }

        /* Add new selected files */
        for (let i=0; i < files.length; i++) {
            var name = files[i].name;

            /* set the name to a limited characters */
            if ( name.length >= 22 ) {
                var shortName = ".." + name.slice(-20);
            }

            var img = "<div class='row file'><div class='col-10 p-2 pl-3'><small class='file-name' full_name='" + name + "'>" + shortName + "</small></div><div class='col-2 p-2 remove-file text-center'><i class='fas fa-times'></i></div></div>"
            $( noFileChosenMsg ).css({'display': 'none'});
            $( noFileChosenMsg ).after(img);
        }

        /* When user removed a file from the panel, after selection */
        $('.remove-file').on('click', function() {
            var smallTag = $(this).parent().find('.file-name')[0]; // contains file name
            var removedFileName = $(smallTag).attr('full_name');

            $(smallTag).parent().parent().remove();    // remove the widget from the panel
            if ( $("#selectedFiles div.file").length == 0 ) {
                $(noFileChosenMsg).css({'display': 'block'});
            }

            // Change the name of the actual File object's name attribute to undefined.
            // Then in the python code, the files with the name <undefined> will be removed before uploading.
//            for (let i=0; i < files.length; i++) {
//                var n = files[i].name;
//                if ( n == removedFileName ) {
//                    Object.defineProperty($('#assignment-submit')[0].files[i], 'name', Object);  // changing the actual file object name
//                    break;
//                }
//            }
        });

        $('#assignmentSubmit').on('click', function(event) {
            if ( $('#selectedFiles').find('div.file').length == 0 ) {
                event.preventDefault();
            }
        });

    });
});

