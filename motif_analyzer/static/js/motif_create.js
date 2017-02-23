$(document).ready(function() {

            /* for adding to motif */
            $('#add_to_motif').click(function() {
                var selectedMotifList = [];

                $(':checkbox:checked').each(function() {
                    selectedMotifList.push($(this).val());
                });

                if (selectedMotifList.length > 1) {
                    var returnString = '';
                    for (var i = 0; i < selectedMotifList.length; i++) {
                        returnString += selectedMotifList[i];
                    }
                    $('#motif').val(($('#motif').val() + '[' + returnString + ']'));
                }
                else if (selectedMotifList.length === 1) {
                    $('#motif').val(($('#motif').val() + selectedMotifList[0]))
                }

                $('input:checkbox').each(function() {
                    this.checked = false;
                })
            });

            /* for clearing motif parts from field and clearing list stored in memory */
            $('#clear_motif').click(function() {
                $('#motif').val('');
            });
        });