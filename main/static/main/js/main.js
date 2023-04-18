$(document).ready( function() {
    /* content wrapper */
    /*$('#wrapper').fadeOut(2)
    $('#wrapper').fadeIn(500);*/

    /* Common interactive elements */
    const sidebar = $('#accordionSidebar');
    const navbar = $("#navbar");
    const contentWrapper = $('#content-wrapper');

    /*
    * Welcome Page
    */
    $('#welcomeImg img').css({'height': $(window).innerHeight() - $(navbar).innerHeight()});

    /* some common values */
    var window_height = $(window).innerHeight();
    var nav_height = $('#navbar').outerHeight();

    /*
    * SITE CONTENT
    */
    var wrapper = $('#wrapper');
    console.log($('#navbar').outerHeight());
    $(wrapper).css({'top': nav_height+'px',});

    /*
    * *   SIDEBAR
    */
    $('#sidebarToggleBtn').on('click', function() {
        $(sidebar).toggleClass('show');
    });
    // When the window is resizing, set the sidebar into initial state.
    $(window).on('resize', function() {
        $(sidebar).removeClass('show');
    });
    // Close the sidebar when clicking outside the sidebar if it is opened
    $('.content-inner').on('click', function() {
        $(sidebar).removeClass('show');
    });
    // When opening the navbar dropdown, close the sidebar if it is opened
    $('#navbarDropdown').on('click', function() {
        $(sidebar).removeClass('show');
    });

    /*
    * MESSAGES
    */
    // Disappear in few seconds
    setInterval(function() {
        $('#messages').slideUp(200);
    }, 3000);

    /*
    *   REGISTRATION FORM
    */

    /* clear the previous form when other form is selecting */
    var lecForm = $('#lecRegisterForm');
    var stuForm = $('#stuRegisterForm');

    $('#lec-form').on('click', function() {
        $(stuForm)[0].reset();
    });
    $('#stu-form').on('click', function() {
        $(lecForm)[0].reset();
    });


    /* Dealing with select option for batch in registration form */
    if ( $('#reg_role').val() == 'Lecturer' ) {
        $('#reg_batch').val(null);
        $('#reg_batch').attr('disabled', 'disabled');
    }

    $('#reg_role').change( function() {
        if ( $(this).val() == 'Lecturer' ) {
            $('#reg_batch').val(null);
            $('#reg_batch').attr('disabled', 'disabled');
        } else {
            $('#reg_batch').attr('disabled', false);
            // Select first value from available options
            var firstOption = $('#reg_batch').children('option')[0];
            $('#reg_batch').val(firstOption.text);
        }
    });

    /* Display the selected assignment files */
    $('#assignment-submit').change( function() {
        var files = $(this)[0].files; // All the selected files (from input field)

        var noFileChosenMsg = $('#noFileChosenMsg');
        $(noFileChosenMsg).css({'display': 'block'});

        // Clear the previous file widgets
        var prevFiles = $("#selectedFiles").find('a');
        for (let i=0; i < prevFiles.length; i++) {
            $(prevFiles[i]).remove();
        }

        // Add new selected files
        for (let i=0; i < files.length; i++) {
            var name = getShortFileName(files[i].name);
            var file = "<a class='border p-2 w-100 d-block rounded shadow-sm'>" + name + "</a>";
            $( noFileChosenMsg ).css({'display': 'none'});
            $( noFileChosenMsg ).after(file);
        }
    });

    /* Add necessary elements to display nice bootstrap file input */
    var customFileInputs = $("input.custom-file-input");

    /* Update the input field with user selected file name */
    $( customFileInputs ).each( function(index, inputElem) {
        $(inputElem).change( function() {
            // If input element has the class <no-inside-name> don't add the name into input field
            if ( ! $(inputElem).hasClass('no-inside-name') ) {
                var selectedFile = $(this)[0].files[0];
                var fileSelected = getShortFileName(selectedFile.name);
                $(this).parent().find('label.custom-file-label').text(fileSelected);
            }
        });
    });

    /* Style each input field properly */
    for (let i=0; i < customFileInputs.length; i++) {
        var input = $(customFileInputs[i]);
        var acceptFilesAttr = $(input).attr('accept');
        var id = $(input).attr('id');

        /*
        *. Find if a file input field has a uploaded file.
        *. If it has, update the input field text with previously uploaded file name.
        */
        var uploadedFileElem = $(input).parent().find('a');
        var uploadedFileName = uploadedFileElem.text();

        var msg = 'Select File';
        if ( uploadedFileName ) {
            splitFileNames = uploadedFileName.split('/');
            msg = splitFileNames[splitFileNames.length - 1]
            msg = getShortFileName(msg);
        } else if (acceptFilesAttr == 'image/*') {
            msg = "Select Image";
        }

        // Add the label that required by bootstrap for file input styling.
        $(input).after("<label class='custom-file-label' for='"+ id +"'>"+ msg +"</label>");
        $(input).parent().addClass('custom-file');  // Bootstrap class

        /* Remove all the unnecessary elements in .custom-file div */
        allElements = $(input).parent().find('br').remove();
        $(input).css({'width': '0px', 'height': '0px'});  // Hide the input tag
        $(uploadedFileElem).hide();  // Anchor element with previously uploaded file link.

        /* Style the top-label and input field */
        $(input).parent().css({'display': 'block'});

        // Don't set the max-width if has the class no-mw
        if ( ! $(input).hasClass('no-mw') ) {
            $(input).parent().css({'max-width': '300px'});
        }

    }

    /*
    * Dealing with items when scrolling
    */

    // Add Question button for quiz edit page
    var addQuizQuestionBtnRow = $('.fixed-internal-row');

    var prevPos = $(document).scrollTop();   // Just as a position detector
    $(document).on('scroll', function() {
        // If nothing found, do not proceed.
        if ( addQuizQuestionBtnRow.length == 0 ) {
            return;
        }

        addQuizQuestionBtnRowPos = addQuizQuestionBtnRow.offset().top;
        var currentPos = $(this).scrollTop();

        if (currentPos > prevPos) {
            prevPos = currentPos;
            // Scrolling Down

            if (addQuizQuestionBtnRowPos < currentPos) {
                $('.fixed-internal-row').css(
                    {'position': 'fixed',
                     'z-index': 20,
                     'padding-top': '20px',
                     'top': nav_height},
                  );
            }

        } else if (currentPos >= prevPos) {
            prevPos = currentPos;
            // Scrolling Up

            if (addQuizQuestionBtnRowPos > currentPos) {
                console.log('Make it sticky');
                $('.fixed-internal-row').css(
                    {'position': 'relative',
                     'z-index': 20,
                     'padding-top': '0px',
                      'top': 0},
                  );
            }
        }
    });

    /*
    * Functions
    */

    function  getShortFileName( fileName ) {
        var splitBySlash = fileName.split('/');
        var name = splitBySlash[splitBySlash.length - 1];
        var shortName = name;

        if ( name.length > 28 ) {
            var shortName = '... ' + name.slice(-20);
        }
        return shortName;
    }

});

