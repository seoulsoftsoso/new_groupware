// console.log("Hello World!");

const txt = {
    // 버튼
    cancel: '취소 되었습니다.',
    create_ed: '등록하였습니다.',
    update_ed: '수정하였습니다.',
    delete_ed: '삭제하였습니다.',
    complete_ed: '완료하였습니다.',
    save_ed: '저장하였습니다.',

    create_will: '등록하시겠습니까?',
    update_will: '수정하시겠습니까?',
    delete_will: '삭제하시겠습니까?',
    delete_will_check: '삭제 하시려면, 삭제 라고 입력하세요.',
    delete_check: '삭제',

    create_select: '등록할 리스트를 선택하세요.',
    update_select: '수정할 리스트를 선택하세요.',
    delete_select: '삭제할 리스트를 선택하세요.',
    list_select: '리스트를 선택하세요.',

    deadline_check: '마감',
    deadline_will: '마감 하시겠습니까?',
    deadline_will_check: '마감 하시려면, 마감 이라고 입력하세요.',

    export_warehouse_will : '[출고수량]이 [해당창고]의 [재고량] 보다 큽니다. 진행하시겠습니까??',

    except: '예외가 발생했습니다.',

    bom_do_not_same: '[BOM 형식의 품번]은 [BOM의 품번]과 동일할 수 없습니다.',

    // 재고현황 이동출고
    item_status_move_amount: '[이동수량]은 0보다 커야 합니다.',
    item_status_same_warehouse: '[출고창고]와 [이동창고]가 동일합니다.',

    // 재고조정
    item_adjust_amount: '[조정수량]을 입력하세요.',

    // 이메일 체크
    chk_email: '이메일 형식을 확인해주세요.',
};

function addrPostCodeFinder(postcodeField, addressField) {
    new daum.Postcode({
        oncomplete: function (data) {
            // 팝업에서 검색결과 항목을 클릭했을때 실행할 코드를 작성하는 부분.
            var finalAddr = '';

            // 각 주소의 노출 규칙에 따라 주소를 조합한다.
            // 내려오는 변수가 값이 없는 경우엔 공백('')값을 가지므로, 이를 참고하여 분기 한다.
            var addr = ''; // 주소 변수
            var extraAddr = ''; // 참고항목 변수

            //사용자가 선택한 주소 타입에 따라 해당 주소 값을 가져온다.
            if (data.userSelectedType === 'R') { // 사용자가 도로명 주소를 선택했을 경우
                addr = data.roadAddress;
            } else { // 사용자가 지번 주소를 선택했을 경우(J)
                addr = data.jibunAddress;
            }

            // 사용자가 선택한 주소가 도로명 타입일때 참고항목을 조합한다.
            if (data.userSelectedType === 'R') {
                // 법정동명이 있을 경우 추가한다. (법정리는 제외)
                // 법정동의 경우 마지막 문자가 "동/로/가"로 끝난다.
                if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
                    extraAddr += data.bname;
                }
                // 건물명이 있고, 공동주택일 경우 추가한다.
                if (data.buildingName !== '' && data.apartment === 'Y') {
                    extraAddr += (extraAddr !== '' ? ', ' + data.buildingName : data.buildingName);
                }
                // 표시할 참고항목이 있을 경우, 괄호까지 추가한 최종 문자열을 만든다.
                if (extraAddr !== '') {
                    extraAddr = ' (' + extraAddr + ')';
                }
                // 조합된 참고항목을 해당 필드에 넣는다.
                finalAddr = addr + extraAddr;

            } else {
                finalAddr = addr;
            }

            // 우편번호를 해당 필드에 넣는다.
            postcodeField.value = data.zonecode;

            // 주소를 해당 필드에 넣는다.
            addressField.value = finalAddr;

        }
    }).open();
}

var getParameters = function (paramName) {
    var returnValue;
    var url = location.href;
    if (url.includes('?')) {
        var parameters = (url.slice(url.indexOf('?') + 1, url.length)).split('&');
        for (var i = 0; i < parameters.length; i++) {
            var varName = parameters[i].split('=')[0];
            if (varName.toUpperCase() == paramName.toUpperCase()) {
                returnValue = parameters[i].split('=')[1];
                return decodeURIComponent(returnValue);
            }
        }
    } else
        return "";
}

function nullapply(value) {
    return ((value === 0 || value) ? value : "");
}

function is_empty(val) {
    // 값이 없으면 true 리턴
    if (val === '') return true;
    if (val === null) return true;
    if (val === undefined) return true;

    return false;  // 값이 존재
}

function numberWithCommas(num) {
    var parts = num.toString().split(".");
    return parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (parts[1] ? "." + parts[1] : "");
}

// 숫자 체크(숫자 이외 값 모두 제거)
function chkNumber(obj){
    var tmpValue = $(obj).val().replace(/[^0-9,]/g,'');
    tmpValue = tmpValue.replace(/[,]/g,'');
    // 천단위 콤마 처리 후 값 강제변경
    obj.value = numberWithCommas(tmpValue);
}

function _numberWithCommas(num, cnt) {
    let point = false;

    if (String(num).includes(".")){
        point = true;
    }

    if (String(num).indexOf('.') == 0 ){
        return '0.';
    }

    if (String(num).indexOf('-.') == 0){
        return '-0.';
    }

    let parts = num.toString().split(".");
    // console.log('parts[0]', parts[0]);
    // console.log('parts[1]', parts[1]);

    let bf = '';  // 소수점 앞
    let af = '';  // 소수점 뒤
    bf = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",")

    if (point == true){
        af = "." + parts[1];

        if ( (cnt*1) <= 2){
            af = af.match(/.{1,3}/);  // 소수점 2자리
        } else if (( (cnt*1) == 3)){
            af = af.match(/.{1,4}/);  // 소수점 3자리
        }
        return bf + af;
    }else{
        return bf;
    }
}

// 숫자 체크(숫자 이외 값 모두 제거)
function _chkNumber(obj, cnt){
    let regexedValue = $(obj).val().replace(/[\{\}\[\]\/?,;:|\)*~`!^a-zA-Z가-힣ㅏ-ㅣㄱ-ㅎ\+_<>@\#$%&\\\=\(\'\"]/g,'');
    let tmpValue = '-';

    // - 중복 삭제
    if (regexedValue[0] !== "-" || regexedValue === '') {
        tmpValue = regexedValue;
    }
    else if (regexedValue[0] === "-") {
        for (let i = 1; i < regexedValue.length; i++){
            if(regexedValue[i] !== '-') tmpValue += regexedValue[i];
        }
    }


    // 천단위 콤마 처리 후 값 강제변경
    obj.value = _numberWithCommas(tmpValue, cnt);
}

// 반올림 함수
function round2(num){
    let ret = 0;
    let f_num = 0.0;
    let i_num = 0;

    try{
        f_num = parseFloat(num);
        i_num = parseInt(num)
    } catch (e){
        return 0;
    }

    let minus = (f_num < 0 ? true : false)
    if (minus == true){
        f_num = f_num * -1;
        i_num = i_num * -1;
    }

    ret = i_num + (f_num - i_num >= 0.5 ? 1.0 : 0.0);

    if (minus == true) {
        ret = ret * -1;
    }

    return ret
}


// 실수형 변환 함수 ( _x : 변환할 값, _y : 허용 소수점 )
function tof(_x, _y) {
    let x = 0.0;

    // _x 가 이상한 기호일 경우
    if (_x == '' || _x == undefined || _x == null) {
        return x;
    }

    if (isNaN(_x) == false) {
        // _x 가 숫자인 경우
        x = _x * 1.0;
    } else {
        try {
            // 콤마가 들어간 문자인 경우
            _x = _x.replace(/,/g, "");

            if (isNaN(_x) == false) {
                x = _x * 1.0;
            } else {
                // 숫자가 아닌 경우
            }
        } catch (e) {
            // 문자인데 다른 문자가 들어간 경우
            console.table('예외', e);
        }
    }
    // console.log('1', x);

    // _y 가 이상한 기호일 경우
    if (_y == '' || _y == undefined || _y == null) {
        _y = 0
    }

    if (isNaN(_y) == false) {
        // _y 가 숫자인 경우
    } else {
        // 숫자가 아닌 경우
        _y = 0
    }

    // 소수점 반올림
    let mul = 1;
    for (let i = 0; i < _y; i++) {
        mul *= 10;
    }

    x = x * mul * 10;
    x = round2(x)  // 소수점 한번 더 에서 반올림
    x = x / 10

    x = round2(x)
    x = x / mul

    return x;
}

function __num(_x) {
    // 천단위 콤마, 반올림 또는 에러를 [실수형]으로 리턴 하는 함수

    // _x 가 이상한 기호일 경우
    if (_x == '' || _x == undefined || _x == null || _x == 'null') {
        return 0;
    }

    if (isNaN(_x) == false) {
        // _x 가 숫자인 경우
        return tof(_x, 3);
    }else{
        // _x 숫자가 아닌경우
        _x = _x.replace(/,/g, "");

        if (isNaN(_x) == false) {
            // _x 가 숫자인 경우
            _x = tof(_x, 3);
            return _x;

        }else{
            // _x 숫자가 아닌경우
            return 0;
        }
    }
}

function __comma(_x){
    let x = __num(_x)
    // 천단위 콤마, 반올림 또는 에러를 [실수형]으로 리턴 하고 >> 천단위 표기로 변경하는 함수
    return x.toLocaleString()
}


function toKR(_number) {
    let pre = ''; // 마이너스인 경우, 마이너스 부호
    let ret = '';

    _number = __num(_number);
    if (_number == 0) {
        return '';
    } // 0 이거나, 숫자가 들어오지 않은 경우 '' 리턴

    _number = (typeof _number !== 'string') ? _number.toString() : _number;

    if (_number.includes('-')) {
        // 마이너스 인경우
        pre = ' ─ ';
        _number = _number.replace(/-/g, '');
    }

    if (_number.includes('.')) {
        // 소수점 포함하는 경우
        let parts = _number.toString().split(".");
        ret = toDigit(parts[0]) + toPoint(parts[1]);

    } else {
        // 소수점이 없는 경우
        ret = toDigit(_number);
    }

    return pre + ret + ' 원';


    // 소수점을 한글로
    function toPoint(number) {
        const krNum = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
        let result = '';
        for (const digit of number) {
            result += krNum[parseInt(digit)];
        }
        return '.' + result;
    }


    // 자연 수를 한글로
    function toDigit(number) {
        var cor = (number.length % 4 === 0) ? 4 : number.length % 4;
        var start = 0;
        var numberSet = [];

        while (true) {
            var temp = number.substr(start, cor);

            if (temp === '') break;

            numberSet.push(temp);
            start = start + cor;
            cor = 4;
        }

        return setMainUnit(numberSet);
    }


    function setMainUnit(ary) {
        var unit = ['경', '조', '억', '만', ''];

        var result = [];
        var cor = unit.length - ary.length;

        for (var i = 0; i < ary.length; i++) {
            var focused = ary[i];
            var u = unit[i + cor];

            if (u == '만' && focused == '0000')
                continue;

            if (u == '억' && focused == '0000')
                continue;

            focused = setSubUnit(focused);
            result.push(focused + u);
        }

        result = result.join(' ');
        return result;
    }


    function setSubUnit(ary) {
        var unit = ['천', '백', '십', ''];
        var numString = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십'];

        var result = '';
        var cor = unit.length - ary.length;

        for (var i = 0; i < ary.length; i++) {
            var u = unit[i + cor];
            var num = numString[ary[i]];

            if (num === '') continue;

            result += num + u;
        }

        return result;
    }
}

function pad(n, cnt) {
    //상세코드가 3자리로 고정될 수 있게 함.

    n = n + "";
    return n.length >= 3 ? n : new Array(3 - n.length + 1).join("0") + n;
}


function _pad(obj, cnt) {
    // Input에 숫자 3자리까지만 입력 받을 수 있도록 하는 함수

    let Value = $(obj).val().replace(/[^0-9,]/g, '');

    if (Value.length > 3) {
        Value = Value.substring(0, 3);
    }

    obj.value = Value;
}

function _bool(_x){
    if ((_x == true) || (_x == 'true') || (_x == 'True')){
        return true;
    }else{
        return false;
    }
}

function _boolt(_x){
    // boolean 을 텍스형으로
    if ((_x == true) || (_x == 'true') || (_x == 'True')){
        return 'true';
    } else {
        return 'false';
    }
}

function _chkDate(date){
    let val = date.value.replace(/\D/g, "");
    let length = val.length;

    let result = '';

    // 5개일때 - 20221 : 바로 출력
    if (length < 6) result = val;
    // 6~7일 때 - 202210 : 2022-101으로 출력
    else if (length < 8) {
        result += val.substring(0, 4);
        result += "-";
        result += val.substring(4);
        // 8개 일 때 - 2022-1010 : 2022-10-10으로 출력
    } else {
        result += val.substring(0, 4);
        result += "-";
        result += val.substring(4, 6);
        result += "-";
        result += val.substring(6);
    }

    // yyyy mm dd 8자 까지만 입력
    if (length > 8) {
        date.value = result.substring(0, 10);  // 하이픈 포함 10자
    }else{
        date.value = result;
    }
}


function _chkEmail(_email) {
    if (_email == '') {
        return true;
    }
    _email = _email.trim();
    _email = _email.toLowerCase();

    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (emailPattern.test(_email)) {
        return true;
    } else {
        return false; // 유효하지 않은 이메일 주소
    }
}


// URL 의 파일명 가져오기
function get_fname(_url) {
    let url = decodeURI(_url);
    let arSplitUrl = url.split("/");    //   "/" 로 전체 url 을 나눈다
    let nArLength = arSplitUrl.length - 1;

    if (nArLength == undefined || nArLength == null || nArLength == -1) {
        return '';
    }

    let sFileName = arSplitUrl[nArLength];   // 나누어진 배열의 맨 끝이 파일명이다
    {
        // console.log('sFileName', sFileName);
    }

    if (sFileName == 'undefined') {
        return '';
    }

    return sFileName;
}


function get_url_extension(url) {
    return url.split(/[#?]/)[0].split('.').pop().trim();
}


function null_empty(_x) {
    let x = _x;
    if (x == null && x == "null" && x == undefined && x == "image1_url") {
        x = "";
    }
    return x;
}


$(function () {

});