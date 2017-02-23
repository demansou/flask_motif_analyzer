$(document).ready(function () {
    /**
     * Gathers filename from full path
     * JavaScript uses `\\` displayed as
     * `C:/fakepath/`
     */
    $("#fasta_file").change(function() {
        var fileName = $(this).val().split('\\').pop();
        $("#file_display").val(fileName);
    })
});