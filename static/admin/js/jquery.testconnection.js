var $ = django.jQuery;


/*
 * Function test_connection
 *
 * This function performs a request to a view that tries to connect to the
 * server specified in the add/modify form in Django administration console.
 * Based on the response to the server indicates that the parameters are correct
 * or wrong and shows a dialog window with this info.
 */

function test_connection (ip, port, username, password) {
    var url = '/server/test/?ip=' + ip + '&port=' + port + '&username=' + username + '&password=' + password;

    $.getJSON(url, function(data) {
        var title = (data.result == true) ? 'Hurra!' : 'Something happened :(';
        jAlert(data.message, title);
    });
}


/*
 * TODO: explain what am I doing here.
 */

$(document).ready(function() {
    $('#testconnection').click(function() {
        var ip = $('#id_ip').val();
        var port = $('#id_port').val();
        var username = $('#id_username').val();
        var password = $('#id_password').val();

        if ($.trim(ip) == '') {
            jAlert("Must complete 'IP' field.", 'Missing parameter');
        }
        else {
            test_connection(ip, port, username, password);
        }
    });
});        
