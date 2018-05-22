/** Global admin object **/
mbbAdmin = {
    color: {
        'green': '#00a65a',
        'gray': '#999999',
        'orange': '#f39c12',
        'red': '#dd4b39',
    },
    list_colors: function(colors, selector) {
        $.each(colors, function(key, value) {
            $('td.field-' + selector + ':contains("' + key + '")')
                .css('color', value);
            $('.admin-filter-' + selector + ' a:contains("' + key + '")')
                .css('color', value);
        });
    },
};

$(document).ready(function($) {
    'use strict';
    $('.sortedm2m-items a').click(function(event) {
        event.preventDefault();
        $(this).prev('input').trigger('click');
    });
    $('.vTimeField').inputmask({
        mask: '99:99:99',
    });
    $('.vDateField').inputmask({
        mask: '9999-99-99',
    });

    /** datarange filter **/
    (function() {
        $('#changelist-filter input[type="reset"]').click(function(event) {
            event.preventDefault();
            var form = $(this).closest('form');
            form.attr('action', window.location.href);
            form.find('input[type="text"]').val('');
            form.submit();
        });
    }());

    /**
     * remember last tab
     */
    (function() {
        $('#tabs').on('tabsactivate', (event, ui) => {
            const form = $(event.target).closest('form');
            if (form.length) {
                localStorage.setItem(
                    'tabs_' + form.prop('id'),
                    ui.newTab.index()
                );
            }
        });
        $('#tabs').on('tabscreate', (event, ui) => {
            const div = $(event.target);
            const form = div.closest('form');
            const hash = window.location.hash.includes('#tabs');
            if (form.length && !hash) {
                let remember = localStorage.getItem('tabs_' + form.prop('id'));
                if (remember !== null) {
                    div.tabs('option', 'active', remember);
                }
            }
        });
    }());

    /**
     * begin & end inputs
     */
    (function() {
        var begin = $('#id_begin_0');
        var end = $('#id_end_0');

        if (!begin.length || !end.length) {
            return;
        }

        begin.on('change, blur', function() {
            if (!end.val()) {
                end.val(begin.val());
            }
        });
    }());

    // admin filter select
    (function() {
        $('.admin-filter-select').change(function() {
            window.location.href = $(this).val();
        });
    }());
});
