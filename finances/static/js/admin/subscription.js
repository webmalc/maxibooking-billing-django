/* global $, mbbAdmin*/
$(document).ready(function() {
    'use strict';
    // Set color for td.field-status
    mbbAdmin.list_colors({
        'enabled': mbbAdmin.color.green,
        'canceled': mbbAdmin.color.red,
    }, 'status');
});
