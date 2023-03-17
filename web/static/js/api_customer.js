// customer.html에 db에 저장된 모든 정보를 띄워줍니다.
function api_get_customer(done_callback) {
    $.ajax({
        url: "/customers/",
        type: "GET",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: { withCredentials: true },
    })
        .done(function (json) {
            done_callback(json);
        })
        .fail(handle_error);
}

//
function api_get_detail_customer(page, customer_code, customer_name, done_callback) {
    $.ajax({
        url: "/customers/?page=" + page + "&division=" + customer_code + "&name=" + customer_name ,
        type: "GET",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: { withCredentials: true },
    })
        .done(function (json) {
            done_callback(json);
        })
        .fail(handle_error);
}

function api_patch_customer(customer_code, allData, done_callback){
    $.ajax({
        url: "/customers/"+customer_code+"/",
        data: allData,
        type: "PATCH",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}
