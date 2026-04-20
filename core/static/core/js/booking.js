document.addEventListener("DOMContentLoaded", function () {
    const occupiedDatesDiv = document.getElementById('occupied-dates');
    if (!occupiedDatesDiv) return;

    let occupiedDates = JSON.parse(occupiedDatesDiv.dataset.dates);
    occupiedDates.sort((a, b) => new Date(a) - new Date(b));

    const checkInInput = document.getElementById("id_check_in");
    const checkOutInput = document.getElementById("id_check_out");
    const guestsInput = document.getElementById("id_guests");
    const nightsField = document.getElementById("nights");
    const totalField = document.getElementById("total");
    const pricePerNight = parseFloat(document.getElementById("price-per-night").value.replace(',', '.'));

    let checkInPicker, checkOutPicker;

    checkInPicker = flatpickr(checkInInput, {
        minDate: "today",
        dateFormat: "Y-m-d",
        locale: "ru",
        disable: occupiedDates,
        onChange: function (selectedDates, dateStr) {
            if (selectedDates.length > 0) {
                const checkInDate = selectedDates[0];

                let minOut = new Date(checkInDate);
                minOut.setDate(minOut.getDate() + 1);
                checkOutPicker.set("minDate", minOut);

                let nextOccupied = occupiedDates.find(d => new Date(d) > checkInDate);

                if (nextOccupied) {
                    checkOutPicker.set("maxDate", nextOccupied);
                } else {
                    checkOutPicker.set("maxDate", null); // Ограничений нет
                }

                if (checkOutInput.value && new Date(checkOutInput.value) <= checkInDate) {
                    checkOutPicker.clear();
                }

                calculate();
            }
        }
    });

    checkOutPicker = flatpickr(checkOutInput, {
        minDate: "today",
        dateFormat: "Y-m-d",
        locale: "ru",
        disable: occupiedDates,
        onChange: function () {
            calculate();
        }
    });

    function updateTotals(nights, total) {
        if(nightsField) nightsField.textContent = nights;
        if(totalField) totalField.textContent = total;
    }

    function calculate() {
        if (checkInInput.value && checkOutInput.value) {
            const start = new Date(checkInInput.value);
            const end = new Date(checkOutInput.value);
            const diffTime = end - start;
            const nights = Math.round(diffTime / (1000 * 60 * 60 * 24));

            if (nights > 0) {
                const guestsCount = parseInt(guestsInput.value) || 1;
                updateTotals(nights, nights * pricePerNight * guestsCount);
            } else {
                updateTotals(0, 0);
            }
        } else {
            updateTotals(0, 0);
        }
    }

    if(guestsInput) guestsInput.addEventListener("change", calculate);

    document.getElementById("booking-form").addEventListener("submit", function(e) {
        if (!checkInInput.value || !checkOutInput.value) {
            e.preventDefault();
            if(window.showErrorToast) window.showErrorToast("Пожалуйста, выберите даты заезда и выезда.");
        }
    });
});