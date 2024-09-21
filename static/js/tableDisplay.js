// displayTable.js

document.addEventListener('DOMContentLoaded', function() {
    var rows = 0;

    function fetchData() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', `/api/fetch_data/${datasetId}/?rows=${rows}`, true);
        xhr.responseType = 'json';

        xhr.onload = function() {
            if (xhr.status === 200) {
                var people = xhr.response;
                var tableHead = document.getElementById('peopleTableHead');
                var tableBody = document.getElementById('peopleTableBody');

                if (people.length > 0) {
                    var headers = Object.keys(people[0]);
                    tableHead.innerHTML = '<tr>' + headers.map(header => `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`).join('') + '</tr>';
                    
                    people.forEach(function(person) {
                        var row = document.createElement('tr');
                        headers.forEach(function(header) {
                            var cell = document.createElement('td');
                            cell.className = header;
                            cell.textContent = person[header];
                            row.appendChild(cell);
                        });
                        tableBody.appendChild(row);
                    });
                }
            } else {
                console.error('Error fetching data: ', xhr.statusText);
            }
        };

        xhr.onerror = function() {
            console.error('Request error');
        };

        xhr.send();
    }

    fetchData();

    document.getElementById('fetchAgain').addEventListener('click', function() {
        rows += 10;
        fetchData();
    });
});
