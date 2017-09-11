/* global $, mbbAdmin*/
$(document).ready(function() {
    'use strict';
    // Set color for td.field-status
    mbbAdmin.list_colors({
        'paid': mbbAdmin.color.green,
        'new': mbbAdmin.color.gray,
        'processing': mbbAdmin.color.orange,
        'canceled': mbbAdmin.color.red,
    }, 'status');
});
