$(document).ready(function($) {
    'use strict';

    (function() {
        // text field filter
        var url = new URI();

        $('.admin-text-field-filter-ul').each(function() {
            var input = $(this).find('.admin-text-field-filter-input');
            var button = $(this).find('.admin-text-field-filter-button');
            var param = button.attr('data-param');
            var search = url.search(true);
            var params = {};
            if (search[param]) {
                input.val(search[param]);
            }
            button.click(function(event) {
                var val = input.val();
                if (!val) {
                    url.removeSearch(param);
                } else {
                    params[param] = val;
                    url.setSearch(params);
                }
                location.replace(url.toString());
            });
        });
    }());
});
