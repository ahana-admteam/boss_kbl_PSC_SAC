// sets max date as today
function setMaxDateForDateInputs() {
    var currentDate = new Date().toISOString().split('T')[0];
    var dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(function (field) {
        field.setAttribute('max', currentDate);
    });
}


// disable e in type=number
function preventExponentialInputForNumberInputs() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('keydown', function (event) {
            if (event.key.toLowerCase() === 'e') {
                event.preventDefault(); // Prevent the default behavior
            }
        });
    });
}

// limit input length
function limitInputLength(inputSelector, maxLength) {
    var inputs = document.querySelectorAll(inputSelector);
    inputs.forEach(function(input) {
        input.addEventListener("input", function() {
            var value = input.value;
            if (value.length > maxLength) {
                input.value = value.slice(0, maxLength);
            }
        });
    });
}

function disableAutocomplete() {
    var inputs = document.querySelectorAll('input');
    
    inputs.forEach(function(input) {
      input.setAttribute('autocomplete', 'off');
    });
  }
  