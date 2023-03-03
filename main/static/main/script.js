$(document).ready(function() {
    /* Set header height properly */
    var window_height = $(window).innerHeight();
    var nav_height = $('#nav').innerHeight();
    $('#header').css('min-height', window_height-nav_height);



    var triggerTabList = [].slice.call(document.querySelectorAll('#myTab a'))
    triggerTabList.forEach(function (triggerEl) {
      var tabTrigger = new bootstrap.Tab(triggerEl)

      triggerEl.addEventListener('click', function (event) {
            event.preventDefault()
            tabTrigger.show()
          })
    })

});

