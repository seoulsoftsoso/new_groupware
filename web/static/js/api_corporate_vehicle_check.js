function checkVehicleAvailability(E_startDate, E_endDate, eventVehicleCode) {
    $.get("/check-vehicle-availability/", {
        start_date: E_startDate,
        end_date: E_endDate
    }, function (data) {
        var $select = $('#vehicle_select');
        $select.empty();
        $.each(data.vehicle_list, function (index, vehicle) {
            var optionText = vehicle.name;
            var optionValue = vehicle.code;
            if (!vehicle.is_available && (!eventVehicleCode || vehicle.code !== eventVehicleCode)) {
                optionText += ' (예약 마감)';
            }
            var $option = $('<option>', {
                value: optionValue,
                text: optionText,
                disabled: !vehicle.is_available && (!eventVehicleCode || vehicle.code !== eventVehicleCode)
            });
            $select.append($option);
        });
        if (eventVehicleCode) {
            $select.val(eventVehicleCode);
        }
    });
}