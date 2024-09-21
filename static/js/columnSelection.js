// columnSelection.js

document.addEventListener('DOMContentLoaded', function() {
    var selectedColumns = [];

    // Function to toggle selection and update UI
    function toggleSelection(column) {
        var index = selectedColumns.indexOf(column);
        if (index === -1) {
            selectedColumns.push(column);
        } else {
            selectedColumns.splice(index, 1);
        }
        updateButtonUI(column);
    }

    // Function to update button UI based on selection
    function updateButtonUI(column) {
        var btn = document.querySelector(`[data-column="${column}"]`);
        if (selectedColumns.includes(column)) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    }

    // Function to generate HTML table
    function generateTable(data) {
        var tableHtml = '<table class="table table-striped"><thead><tr>';
        selectedColumns.forEach(function(column) {
            tableHtml += `<th>${column}</th>`;
        });
        tableHtml += '<th>Count</th></tr></thead><tbody>';
        data.forEach(function(item) {
            tableHtml += '<tr>';
            selectedColumns.forEach(function(column) {
                tableHtml += `<td>${item[column]}</td>`;
            });
            tableHtml += `<td>${item['count']}</td></tr>`;
        });
        tableHtml += '</tbody></table>';
        return tableHtml;
    }

    // Event listener for column buttons
    var columnButtons = document.querySelectorAll('.column-btn');
    columnButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var column = button.dataset.column;
            toggleSelection(column);
        });
    });

    // Event listener for Count button
    document.getElementById('countBtn').addEventListener('click', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', `/api/count_occurrences/${datasetId}/?columns=${selectedColumns.join(',')}`, true);
        xhr.responseType = 'json';  // Expecting JSON response from server

        xhr.onload = function() {
            if (xhr.status === 200) {
                var counts = xhr.response;
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<h2>Occurrences</h2>' + generateTable(counts);
            } else {
                console.error('Error fetching data: ', xhr.statusText);
            }
        };

        xhr.onerror = function() {
            console.error('Request error');
        };

        xhr.send();
    });
});
