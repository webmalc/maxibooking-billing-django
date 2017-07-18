/* global $*/
$(document).ready(function() {
    'use strict';
    // Set color for td.field-status
    (function() {
        var colors = {
            'active': '#00a65a',
            'not confirmed': '#999999',
            'disabled': '#f39c12',
            'archived': '#dd4b39'};

        $.each(colors, function(key, value) {
            $('td.field-status:contains("'+ key +'")').css('color', value);
            $('.admin-filter-status a:contains("'+ key +'")')
                .css('color', value);
        });
    }());
});
