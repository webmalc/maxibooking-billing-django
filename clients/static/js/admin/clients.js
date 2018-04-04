/* global $, mbbAdmin*/
$(document).ready(function() {
    'use strict';
    // Set color for td.field-status
    mbbAdmin.list_colors({
        'active': mbbAdmin.color.green,
        'not confirmed': mbbAdmin.color.gray,
        'disabled': mbbAdmin.color.orange,
        'archived': mbbAdmin.color.red,
    }, 'status');

    // Generate login link
    (function() {
        var input = $('input#id_login');
        console.log(input);
        if (!input.length) {
            return;
        }
        var link = $('<span/>', {
            id: 'login-generate',
            title: 'Generate login',
            text: 'generate',
        }).click(function() {
            if (!input.val()) {
                input.val('temp-' + new Date().getTime());
            }
        });
        input.after(link);
    }());
});
