$(document).ready( function() {
    /* Set header height properly */
    var window_height = $(window).innerHeight();
    var nav_height = $('#nav').outerHeight();
    $('#header').css('min-height', window_height-nav_height);

    /* Common interactive elements */
    const sidebar = $('#accordionSidebar');
    const navbar = $("#nav");
    const contentWrapper = $('#content-wrapper');

    // set positions of main elements at page load
    setContentPos();

    /*
    *  NAVBAR
    */
    $('#navToggle').on('click', function() {
        var navToggler = $(this);

        // Get the target content from data-target attribute
        var targetMenuAttr = $(this).attr('data-target');
        var targetMenu = $(targetMenuAttr);

        // All the dropdown-menus inside the target menu
        var dropdownMenus = $(targetMenu).find('.dropdown-menu');

        // All the dropdown togglers
        var dropdownTogglers = $("a[data-toggle='dropdown']");

        if ( $(navToggler).attr('aria-expanded') == 'false' ) {
            // Area is collapsed but going to be expanded
            // Show all the dropdown menus inside the target content
            $(dropdownMenus).each( function(index, item) {
                $(item).addClass('display-dropdown');
            });

            // Hide all the dropdown toggler links
            $(dropdownTogglers).each( function(index, item) {
                $(item).css({'display': 'none'});
            });
        } else {
            // Area is expanded but going to be collapsed
            // Hide all the dropdown menus inside the target content
            $(dropdownMenus).each( function(index, item) {
                $(item).removeClass('display-dropdown');
            });

            // Show all the dropdown toggler links
            $(dropdownTogglers).each( function(index, item) {
                $(item).css({'display': 'block'});
            });
        }
    });

    /*
    *   SIDEBAR
    */
    // Additional toggle action
    $('#toggleSideNav').on('click', function() {
        $('ul.sidebar').toggleClass('toggled');
    });

    // Put all the necessary functions that needs to be run, when window resizing.
    $(window).on('resize', function() {
        setContentPos();
    });

    /*
    When Scrolling down slide-up navbar. When scrolling up slide-sown the navbar
    */
    var lastScrollTop = 0;
    $(document).on('scroll', function() {
        var st = $(this).scrollTop(); // Current top position
        if ( st > lastScrollTop ) {
            // Scrolling Down
            $(navbar).slideUp(150);
            $(sidebar).css({'top': 0});
            $(contentWrapper).css({'top': 0});
            lastScrollTop = st;
        } else {
            // Scrolling Up
            $(navbar).slideDown(150);
            $(sidebar).css({'top': nav_height});
            lastScrollTop = st;
        }
    });

    /*
    * MESSAGES
    */
    // Disapear in few seconds
    setInterval(function() {
        $('#messages').slideUp(200);
    }, 3000);

    /*
    *   REGISTRATION FORM
    */
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

    /* Functions */
    function  getShortFileName( fileName ) {
        var splitBySlash = fileName.split('/');
        var name = splitBySlash[splitBySlash.length - 1];
        var shortName = name;

        if ( name.length > 28 ) {
            var shortName = '... ' + name.slice(-20);
        }
        return shortName;
    }

    function setContentPos() {
        /* Set the site main content and footer position properly. Important */
        var sidebarWidth = $(sidebar).innerWidth();
        var windowWidth = $(window).innerWidth();

        var contentWidth = windowWidth - sidebarWidth;
        $('#content-wrapper').css({'width': contentWidth});    // Set main content width
        $('#content-wrapper').css({'margin-left': windowWidth-contentWidth});    // Set main content margin-left
        $('#content-wrapper').slideDown(350);

        /* Set the wrapper top position */
        $('#wrapper').css({'position': 'relative', 'top': nav_height + 'px'});
    }


});

