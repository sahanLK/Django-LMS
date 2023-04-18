var countDownElem = $('#quizTImeCounter');

// gathering information for countDownTIme
var splittedDate = $('#start').val().split(' ');
var year = $.trim(splittedDate[2].replace(',', ''));
var month = $.trim(splittedDate[0]);
var day = splittedDate[1].replace(',', '');



// gathering time info from text in display
var splitCounter = $.trim($('#quizTImeCounter').text()).split(',');
var timeSplit = splitCounter[splitCounter.length - 1].toString().split(':');
var hour = timeSplit[0];
var min = timeSplit[1];
var sec = timeSplit[2];



// Set the date we're counting down to
var dateStr = `${month} ${day}, ${year} ${hour}:${min}:${sec}`;
console.log(dateStr);

var countDownDate = new Date(dateStr).getTime();

function timeCounter() {
    // Get today's date and time
    var now = new Date().getTime();

    // Find the distance between now and the count down date
    var distance = countDownDate;

    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Set into 2 digits format
    hours = (hours < 10)? '0'+hours: hours;
    minutes = (minutes < 10)? '0'+minutes: minutes;
    seconds = (seconds < 10)? '0'+seconds: seconds;

    // Display the result in the element with id="demo"
    var newCountdown = days + " days, " + hours + ":" + minutes + ":" + seconds;
    countDownElem.text(newCountdown);

    // If the count down is finished, write some text
    if (distance < 0) {
        clearInterval(x);
        countDownElem.text("Started");
    }
}


// Update the count down every 1 second
var x = setInterval(timeCounter, 1000);
