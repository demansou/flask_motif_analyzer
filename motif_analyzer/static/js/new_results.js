$(document).ready(function () {
    startAnalysis();
    highlightMotifs();
    $("#next-results").click(function () {
        displayNextResults(resultsBuffer);
        if (parseInt($("#endIndex").val()) >= resultsBuffer.length) {
            $("#next-results").attr('disabled', true);
        }
        if (parseInt($("#startIndex").val()) > 0) {
            $("#prev-results").attr('disabled', false);
        }
    });
    $("#prev-results").click(function () {
        displayPrevResults(resultsBuffer);
        if (parseInt($("#startIndex").val()) <= 0) {
            $("#prev-results").attr('disabled', true);
        }
        if (parseInt($("#endIndex").val()) < resultsBuffer.length) {
            $("#next-results").attr('disabled', false);
        }
    });
});

var interval = null;
var resultsBuffer = null;

function startAnalysis () {
    $.post('/start_analysis/').done(function (data) {
        data = JSON.parse(data);
        console.log(data);
        if (data.redirect) {
            document.location.href = data.redirect;
        }
        else {
            interval = setInterval(countResults, 1000);
        }
    });
}

function countResults () {
    $.post('/count_results/').done(function (data) {
        data = JSON.parse(data);
        console.log(data);
        if (data.redirect) {
            document.location.href = data.redirect;
        }
        else if (!data.complete) {
            $("#task_progress").text(data.message);
        }
        else {
            $("#task_progress").text(data.message);
            $('#analysis_completed').text('Completed!');
            clearInterval(interval);
            interval = setInterval(getResults, 5000);
        }
    })
}

function getResults () {
    $.post('/get_results/').done(function (data) {
        data = JSON.parse(data);
        console.log(data);
        if (data.redirect){
            document.location.href = data.redirect;
        }
        else if (data.data.length > 0) {
            clearInterval(interval);
            resultsBuffer = displayResultsStart(data.data);
            $("#download_link").show().fadeIn(1000);
        }
    })
}

function displayResultsStart (htmlResults) {
    var limit = $("#endIndex").val();
    if (htmlResults.length < $("#endIndex").val()) {
        limit = htmlResults.length;
    }
    for (var i = 0; i < limit; i++) {
        $("#results").append(htmlResults[i]);
    }
    if (parseInt($("#endIndex").val()) < htmlResults.length) {
        $("#next-results").attr('disabled', false);
    }
    return htmlResults;
}

function displayNextResults (htmlResults) {
    increaseIndexes();
    var limit = $("#endIndex").val();
    if (htmlResults.length < $("#endIndex").val()) {
        limit = htmlResults.length;
    }
    $("#results").empty();
    for (var i = $("#startIndex").val(); i < limit; i++) {
        $("#results").append(htmlResults[i]);
    }
}

function displayPrevResults (htmlResults) {
    if ($("#startIndex").val() < 0) {

    }
    decreaseIndexes();
    $("#results").empty();
    for (var i = $("#startIndex").val(); i < $("#endIndex").val(); i++) {
        $("#results").append(htmlResults[i]);
    }
}

function increaseIndexes() {
    $("#startIndex").val(parseInt($("#startIndex").val()) + 50);
    console.log($("#startIndex").val());
    $("#endIndex").val(parseInt($("#endIndex").val()) + 50);
    console.log($("#endIndex").val());
}

function decreaseIndexes() {
    $("#startIndex").val(parseInt($("#startIndex").val()) - 50);
    console.log($("#startIndex").val());
    $("#endIndex").val(parseInt($("#endIndex").val()) - 50);
    console.log($("#endIndex").val());
}

function highlightMotifs () {
    $.initialize(".motif-string", function () {
        var re = new RegExp($(this).attr('id'));
        $(this).highlightRegex(re);
    });
}