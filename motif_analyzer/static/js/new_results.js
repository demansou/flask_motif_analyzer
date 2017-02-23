$(document).ready(function () {
    startAnalysis();
    highlightMotifs();
    $("#next-results").click(function () {
        displayNextResults(resultsBuffer);
    });
    $("#prev-results").click(function () {
        displayPrevResults(resultsBuffer);
    });
});

var interval = null;
var resultsBuffer = null;
var startIndex = 0, endIndex = 0;

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
            getResults();
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
        else {
            $("#download_link").show().fadeIn(1000);
            if (data.data.length > 0) {
                console.log('should append data');
                resultsBuffer = displayResultsStart(data.data);
            }
        }
    })
}

function displayResultsStart (htmlResults) {
    var limit = endIndex;
    if (htmlResults.length < endIndex) {
        limit = htmlResults.length;
    }
    for (var i = 0; i < limit; i++) {
        console.log(htmlResults[i]);
        $("#results").append(htmlResults[i]);
    }
    return htmlResults;
}

function displayNextResults (htmlResults) {
    var newIndexes = increaseIndexes(startIndex, endIndex);
    startIndex = newIndexes.start;
    endIndex = newIndexes.end;
    var limit = endIndex;
    if (htmlResults.length < endIndex) {
        limit = htmlResults.length;
    }
    $("#results").empty();
    for (var i = startIndex; i < limit; i++) {
        $("#results").append(htmlResults[i]);
    }
}

function displayPrevResults (htmlResults) {
    var newIndexes = decreaseIndexes(startIndex, endIndex);
    startIndex = newIndexes.start;
    endIndex = newIndexes.end;
    if (startIndex < 0) {
        newIndexes = increaseIndexes(startIndex, endIndex);
        startIndex = newIndexes.start;
        endIndex = newIndexes.end;
    }
    var limit = endIndex;
    $("#results").empty();
    for (var i = startIndex; i < limit; i++) {
        $("#results").append(htmlResults[i]);
    }
}

function increaseIndexes(oldStartIndex, oldEndIndex) {
    return {start: oldStartIndex + 50, end: oldEndIndex + 50}
}

function decreaseIndexes(oldStartIndex, oldEndIndex) {
    return {start: oldStartIndex - 50, end: oldEndIndex - 50}
}

function highlightMotifs () {
    $.initialize(".motif-string", function () {
        var re = new RegExp($(this).attr('id'));
        $(this).highlightRegex(re);
    });
}