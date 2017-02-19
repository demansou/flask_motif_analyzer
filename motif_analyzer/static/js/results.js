function startAnalysis (interval) {
    $.post('/start_analysis/').done(function (data) {
        data = JSON.parse(data);
        if (data.error === true || data.started === false) {
            $("#results_error").text(data.message).show().fadeIn(1000);
        }
        else {
            interval = setInterval(countResults(interval), 5000);
        }
    });
}

function countResults (interval) {
    $.post('/count_results/').done(function (data) {
        data = JSON.parse(data);
        if (data.error === true) {
            $("#results_error").text(data.message).show().fadeIn(1000);
        }
        else {
            clearInterval(interval);
            $('#analysis_completed').text('Completed!');
            getResults();
        }
    })
}

function getResults () {
    $.post('/get_results/').done(function (data) {
        data = JSON.parse(data);
        var resultsDataArray = data.data;
        $("#download_link").show().fadeIn(1000);
        for (var i = 0; i < resultsDataArray.length; i++) {
            $('#results').append(generateHTML(resultsDataArray[i]));
        }
    })
}

function generateHTML (result) {
    // if no motifs, do not generate HTML
    if (result.has_motif === false) {
        return '';
    }

    var sequenceDescription = result.sequence_description;
    var sequence = result.sequence;
    var analysis = result.analysis;
    var innerTableHTML = generateInnerTableHTML(analysis, sequence, sequenceDescription);
    return generateOuterTableHTML(sequenceDescription, innerTableHTML);
}

function generateOuterTableHTML (sequenceDescription, innerTableHTML) {
    return "<table class=\"table table-bordered table-responsive\">"
        + "<tr><td width=\"15%\"><strong>Sequence ID</strong></td><td width=\"85%\" "
        + "class=\"is-breakable\">" + sequenceDescription + "</td></tr><tr><td>"
        + "<strong>Motif Matches</strong></td><td class=\"\">"
        + innerTableHTML + "</td></tr></table>";
}

function generateInnerTableHTML (analysis, sequence, sequenceDescription) {
    var innerTableHTML = '';
    for (var i = 0; i < analysis.length; i++) {
        for (var key in analysis[i]) {
            var analysisHTML = generateAnalysisHTML(analysis[i][key], sequence, sequenceDescription, key);
            innerTableHTML += "<table class=\"table table-bordered table-responsive\">"
                + "<tr><td width=\"10%\"><strong>Motif</strong></td><td width=\"70%\" class=\"is-breakable\">"
                + key + "</td><td width=\"20%\"></td></tr>" + analysisHTML + "</table>";
        }
    }
    return innerTableHTML;
}

function generateAnalysisHTML (analysisKeyValue, sequence, sequenceDescription, key) {
    var analysisResultArray = parseAnalysis(analysisKeyValue);
    var analysisHTML = '';
    for (var i = 0; i < analysisResultArray.length; i++) {
        var modalId = randomString(16, "#aA");
        var modalHTML = generateModalHTML(analysisResultArray[i][1], analysisResultArray[i][2], sequence, sequenceDescription, modalId, key);
        analysisHTML += "<tr><td></td><td class=\"is-breakable\">"
            + analysisResultArray[i][0] + "</td><td>"
            + "<button type=\"button\" class=\"btn btn-primary btn-block\" "
            + "data-toggle=\"modal\" data-target=\"#" + modalId + "\">"
            + "View Motif</button>" + modalHTML + "</td></tr>";
    }
    return analysisHTML;
}

function generateModalHTML (subsequenceStart, subsequenceEnd, sequence, sequenceDescription, modalId, key) {
    var parsedSequence = generateParsedSequence(subsequenceStart, subsequenceEnd, sequence, key);
    return "<div class=\"modal modal-fullscreen fade\" id=\"" + modalId + "\" "
        + "role=\"dialog\" aria-hidden=\"true\"><div class=\"modal-dialog\">"
        + "<div class=\"modal-content\"><div class=\"modal-header\">"
        + "<button type=\"button\" class=\"close\" data-dismiss=\"modal\">"
        + "<span aria-hidden=\"true\">&times;</span><span class=\"sr-only\">Close</span></button>"
        + "<h4 class=\"modal-title\">" + sequenceDescription + "</h4>"
        + "</div><div class=\"modal-body\"><p class=\"is-breakable\">" + parsedSequence + "</p></div>"
        + "</div></div></div>";
}

function generateParsedSequence(subsequenceStart, subsequenceEnd, sequence, key) {
    var sequenceMotif = "<strong><span class=\"motif-string\" id=\"" + key +"\">"
        + sequence.substring(subsequenceStart, subsequenceEnd) + "</span></strong>";
    var parsedSequence = [];
    parsedSequence.push(sequence.substring(0, subsequenceStart));
    parsedSequence.push(sequenceMotif);
    parsedSequence.push(sequence.substring(subsequenceEnd, sequence.length));
    return parsedSequence.join("");

}

function analysisKeyValueToString(analysisKeyValue) {
    var analysisKeyValueString = '';
    for (var i = 0; i < analysisKeyValue.length; i++) {
        analysisKeyValueString += "Match: \"" + analysisKeyValue[i].match
            + "\", Span: [" + analysisKeyValue[i].span[0] + ","
            + analysisKeyValue[i].span[1] + "]<br>";
    }
    return analysisKeyValueString;
}

function motifStartPos (analysisKeyValue) {
    return analysisKeyValue[0].span[0];
}

function motifEndPos (analysisKeyValue) {
    return analysisKeyValue[analysisKeyValue.length - 1].span[1];
}

function parseAnalysis (analysisKeyValue) {
    var analysisResultArray = [];
    for (var i = 0; i < analysisKeyValue.length; i++) {
        var analysisKeyValueString = analysisKeyValueToString(analysisKeyValue[i]);
        var subsequenceStart = motifStartPos(analysisKeyValue[i]);
        var subsequenceEnd = motifEndPos(analysisKeyValue[i]);
        analysisResultArray.push([analysisKeyValueString, subsequenceStart, subsequenceEnd])
    }
    return analysisResultArray;
}

function randomString(length, chars) {
    var mask = '';
    if (chars.indexOf('a') > -1) mask += 'abcdefghijklmnopqrstuvwxyz';
    if (chars.indexOf('A') > -1) mask += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (chars.indexOf('#') > -1) mask += '0123456789';
    if (chars.indexOf('!') > -1) mask += '~`!@#$%^&*()_+-={}[]:";\'<>?,./|\\';
    var result = '';
    for (var i = length; i > 0; --i) {
        result += mask[Math.floor(Math.random() * mask.length)];
    }
    return result;
}

function highlightMotifs () {
    $.initialize(".motif-string", function () {
        var re = new RegExp($(this).attr('id'));
        $(this).highlightRegex(re);
    });
}