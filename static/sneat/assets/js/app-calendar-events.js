let events_data = []

  function getDatas() {
      return new Promise((resolve, reject) => {

          api_gp("/event/get_event_all/", "GET", {}, (done) => {
              if (done.error) {
                  reject('Error');
              } else {
                  let data = done.result;

                  for (let i = 0; i < data.length; i++) {
                      let item = data[i];
                      let participants = item.participants;

                      let obj = {
                          id: item.id,
                          url: item.url,
                          title: item.title,
                          start: new Date(item.start_date),
                          end: new Date(item.end_date),
                          allDay: item.allDay,
                          extendedProps: {
                              calendar: item.event_type,
                              location: item.location,
                              description: item.description,
                              created_by: item.create_by__username,
                              guests: participants,
                              vehicle: item.vehicleSelect,
                              vehicleName: item.vehicleName
                          },
                          businessPair: item.businessPair,
                      };

                      events_data.push(obj);
                  }
                  // console.log('obj', events_data)
                  if (typeof displayData === "function") {
                      displayData(events_data);
                  }
                  resolve(events_data);
              }
          });
      });
  }
/*
  function handleEventsData(data) {
    // 여기서 data를 사용하여 필요한 작업 수행
    alert('bbbbbb');
    events_data = data;

    // 예: 달력에 이벤트 추가 등
  }
  getDatas().then(events_data => {

      handleEventsData(events_data);
      // currentEvents로 무언가를 수행
  }).catch(error => {
      console.error(error);
      // 에러 처리
  });*/
/*

let date = new Date();
let nextDay = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
// prettier-ignore
let nextMonth = date.getMonth() === 11 ? new Date(date.getFullYear() + 1, 0, 1) : new Date(date.getFullYear(), date.getMonth() + 1, 1);
// prettier-ignore
let prevMonth = date.getMonth() === 11 ? new Date(date.getFullYear() - 1, 0, 1) : new Date(date.getFullYear(), date.getMonth() - 1, 1);


let events = [
     {
    id: 10,
    url: '',
    title: 'Monthly Checkup',
    start: nextDay,
    end: nextDay,
    allDay: true,
    extendedProps: {
      calendar: 'Personal'
    }
  }
]*/
