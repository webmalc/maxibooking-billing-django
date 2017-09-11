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
});
