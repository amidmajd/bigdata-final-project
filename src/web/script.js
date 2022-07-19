var last_hour = document.getElementById("last_hour_data");
var last_6_hour = document.getElementById("last_6_hour_data");
var last_6_hour_by_loc = document.getElementById("last_6_hour_by_loc_data");
var total_trips_in_period = document.getElementById("total_trips_in_period_data");
var table_body = document.getElementById("table_body");

var loc_input = document.getElementById("loc-input");
var start_input = document.getElementById("start-input");
var end_input = document.getElementById("end-input");
var loc_submit_btn = document.getElementById("loc_submit_btn");
var period_submit_btn = document.getElementById("period_submit_btn");

const API_BASE_URL = "http://127.0.0.1:9090/api";
let LOC_SET = false;
let PERIOD_SET = false;
let trips_prev = [];

set_values = () => {
  fetch(API_BASE_URL + "/trip/count/total")
    .then((response) => response.json())
    .then((data) => (last_hour.innerText = data.total_trip_count));

  fetch(API_BASE_URL + "/trip/count")
    .then((response) => response.json())
    .then((data) => (last_6_hour.innerText = data.total_trip_count));

  fetch(API_BASE_URL + "/trip/latest/1000")
    .then((response) => response.json())
    .then((data) => {
      trips = data["1000_latest_trips"];
      let trips_diff = _.differenceWith(trips, trips_prev, _.isEqual);
      trips_prev = trips_prev.concat(trips_diff);

      trips_diff.forEach((row) => {
        let datetime = new Date(row.timestamp * 1000);
        table_row = `
      <tbody id="table_body">
      <tr>
        <td class="column1">${row.uuid}</td>
        <td class="column2">${datetime.toLocaleString()}</td>
        <td class="column3">${row.Lat}</td>
        <td class="column4">${row.Lon}</td>
        <td class="column5">${row.Base}</td>
      </tr>`;
        table_body.innerHTML = table_row + table_body.innerHTML;
      });
    });

  if (LOC_SET) {
    fetch(API_BASE_URL + "/trip/count" + `?location=${loc_input.value}`)
      .then((response) => response.json())
      .then((data) => (last_6_hour_by_loc.innerText = data.trip_count));
  }

  if (PERIOD_SET) {
    fetch(API_BASE_URL + "/trip/count" + `?start=${start_input.value}&end=${end_input.value}`)
      .then((response) => response.json())
      .then((data) => (total_trips_in_period.innerText = data.total_trip_count));
  }
};

loc_submit_btn.addEventListener("click", () => {
  LOC_SET = true;
  fetch(API_BASE_URL + "/trip/count" + `?location=${loc_input.value}`)
    .then((response) => response.json())
    .then((data) => (last_6_hour_by_loc.innerText = data.trip_count));
});

period_submit_btn.addEventListener("click", () => {
  PERIOD_SET = true;
  fetch(API_BASE_URL + "/trip/count" + `?start=${start_input.value}&end=${end_input.value}`)
    .then((response) => response.json())
    .then((data) => (total_trips_in_period.innerText = data.total_trip_count));
});

set_values();
setInterval(set_values, 2000);
