const slider = document.getElementById('roomsSlider');

if (slider) {
    function moveSlider(direction) {
        const firstCard = slider.querySelector('.room-card');
        if (!firstCard) return;

        const cardWidth = firstCard.offsetWidth + 32;
        const currentScroll = slider.scrollLeft;

        if (direction === 1 && currentScroll + slider.offsetWidth >= slider.scrollWidth - 10) {
            slider.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            slider.scrollBy({ left: direction * cardWidth, behavior: 'smooth' });
        }
    }

    let autoScroll = setInterval(() => moveSlider(1), 3000);

    slider.addEventListener('mouseenter', () => clearInterval(autoScroll));
    slider.addEventListener('mouseleave', () => {
        autoScroll = setInterval(() => moveSlider(1), 3000);
    });
}

function showMoreRooms() {
        const hiddenRooms = document.querySelectorAll('.hidden-room');
        const nextBatch = 3;

        for (let i = 0; i < nextBatch && i < hiddenRooms.length; i++) {
            hiddenRooms[i].style.display = 'flex';
            hiddenRooms[i].classList.remove('hidden-room');
        }

        if (document.querySelectorAll('.hidden-room').length === 0) {
            document.getElementById('loadMoreContainer').style.display = 'none';
        }
    }
